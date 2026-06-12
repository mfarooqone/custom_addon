import json

from odoo import http
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.http import request


class CrmApi(http.Controller):
    """HTTP entry points for external CRM systems.

    Contact APIs use auth='none' because authentication is done with the
    company CRM API key (see res.partner._crm_authenticate_company).
    csrf=False is required for external POST/PUT calls without an Odoo session.
    """

    def _json(self, payload, status=200):
        """Return a JSON HTTP response."""
        return request.make_response(
            json.dumps(payload, default=str),
            headers=[('Content-Type', 'application/json')],
            status=status,
        )

    def _error(self, error):
        """Map Odoo exceptions to HTTP status codes for API clients."""
        message = error.args[0] if error.args else str(error)
        if isinstance(message, dict):
            message = message.get('message', str(message))
        text = str(message)
        if isinstance(error, AccessError):
            # Invalid/missing key -> 401; blocked contact (company user) -> 403
            status = 401 if 'API key' in text else 403
        elif isinstance(error, ValidationError):
            status = 404 if 'not found' in text.lower() else 400
        elif isinstance(error, UserError):
            status = 400
        else:
            status = 500
        return self._json({'success': False, 'error': message}, status=status)

    def _partners(self, company):
        """Partner recordset scoped to the authenticated company."""
        return request.env['res.partner'].sudo().with_company(company)

    def _success(self, partner, status=200):
        return self._json({'success': True, 'data': partner._crm_api_serialize()}, status=status)

    @http.route('/api/crm/v1/contacts', type='http', auth='none', methods=['POST'], csrf=False)
    def create_contact(self, **kwargs):
        """Create a contact. Requires name + contact_type in JSON body."""
        try:
            Partner = request.env['res.partner'].sudo()
            company = Partner._crm_authenticate_company(request)
            partner = self._partners(company).create(
                Partner._crm_prepare_partner_vals(
                    Partner._crm_parse_json_body(request),
                    for_create=True,
                )
            )
            # custom_contacts assigns CUST/VEND/EMP IDs on create via contact_type
            return self._success(partner, status=201)
        except Exception as error:
            return self._error(error)

    @http.route(
        '/api/crm/v1/contacts/<int:partner_id>',
        type='http',
        auth='none',
        methods=['PUT'],
        csrf=False,
    )
    def update_contact(self, partner_id, **kwargs):
        """Update an existing contact. Send only fields to change."""
        try:
            Partner = request.env['res.partner'].sudo()
            company = Partner._crm_authenticate_company(request)
            payload = Partner._crm_parse_json_body(request)
            if not payload:
                raise ValidationError('Request body is required.')

            partner = self._partners(company).browse(partner_id).exists()
            if not partner:
                raise ValidationError('Contact not found.')
            partner._crm_api_check_writable()
            vals = Partner._crm_prepare_partner_vals(payload)
            if vals:
                partner.write(vals)
            return self._success(partner)
        except Exception as error:
            return self._error(error)

    @http.route('/crm_integration/api/docs', type='http', auth='user', methods=['GET'])
    def api_docs(self, **kwargs):
        """In-app API reference (requires logged-in Odoo user)."""
        return request.render('crm_integration.crm_api_doc_page', {
            'base_url': request.httprequest.host_url.rstrip('/'),
        })

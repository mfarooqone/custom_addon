from odoo import api, models
from odoo.exceptions import AccessError, ValidationError

# Allowed values for contact_type (from custom_contacts module)
CONTACT_TYPES = frozenset({'customer', 'vendor', 'employee'})

# Partner fields accepted directly from JSON (no extra lookup)
PARTNER_API_FIELDS = (
    'name', 'email', 'phone', 'mobile', 'street', 'street2', 'city', 'zip',
    'vat', 'website', 'comment', 'ref', 'company_name',
)

# Boolean fields from JSON payload
PARTNER_API_BOOL_FIELDS = ('is_company', 'active')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # -------------------------------------------------------------------------
    # Authentication & request parsing
    # -------------------------------------------------------------------------

    @api.model
    def _crm_get_api_key(self, request):
        api_key = request.httprequest.headers.get('X-CRM-API-Key', '').strip()
        if api_key:
            return api_key
        authorization = request.httprequest.headers.get('Authorization', '')
        if authorization.startswith('Bearer '):
            return authorization[7:].strip()
        return ''

    @api.model
    def _crm_authenticate_company(self, request):
        """Validate API key and return the matching company.

        Key can be sent as:
        - Header: X-CRM-API-Key
        - Header: Authorization: Bearer <key>

        Integration must be enabled on the company (Settings -> CRM Integration).
        """
        api_key = self._crm_get_api_key(request)
        if not api_key:
            raise AccessError('Missing API key. Use X-CRM-API-Key or Authorization: Bearer <key>.')
        company = self.env['res.company'].sudo().search([
            ('crm_api_key', '=', api_key),
            ('is_crm_integration_enabled', '=', True),
        ], limit=1)
        if not company:
            raise AccessError('Invalid API key or CRM integration is disabled for this company.')
        return company

    @api.model
    def _crm_parse_json_body(self, request):
        """Read and validate the JSON request body."""
        if not request.httprequest.data:
            return {}
        payload = request.httprequest.get_json(force=True, silent=True)
        if payload is None:
            return {}
        if not isinstance(payload, dict):
            raise ValidationError('JSON body must be an object.')
        return payload

    # -------------------------------------------------------------------------
    # Create / update payload
    # -------------------------------------------------------------------------

    @api.model
    def _crm_normalize_contact_type(self, contact_type):
        if contact_type is None:
            return None
        contact_type = str(contact_type).lower()
        if contact_type not in CONTACT_TYPES:
            raise ValidationError('contact_type must be one of: customer, vendor, employee.')
        return contact_type

    @api.model
    def _crm_resolve_country(self, country_code):
        country = self.env['res.country'].sudo().search([
            ('code', '=', str(country_code).upper()),
        ], limit=1)
        if not country:
            raise ValidationError(f'Unknown country code: {country_code}')
        return country.id

    @api.model
    def _crm_resolve_state(self, country_id, state_name=None, state_code=None):
        if not country_id:
            raise ValidationError('country_code is required when sending state_name or state_code.')
        domain = [('country_id', '=', country_id)]
        domain.append(
            ('code', '=', str(state_code).upper()) if state_code else ('name', '=ilike', state_name)
        )
        state = self.env['res.country.state'].sudo().search(domain, limit=1)
        if not state:
            raise ValidationError('Unknown state for the given country.')
        return state.id

    @api.model
    def _crm_prepare_partner_vals(self, payload, *, for_create=False):
        """Build res.partner write/create values from API JSON.

        On create: name and contact_type are required.
        country_code / state_name / state_code are resolved to Odoo IDs.
        """
        if for_create:
            for field_name in ('name', 'contact_type'):
                if not payload.get(field_name):
                    raise ValidationError(f'{field_name} is required.')

        contact_type = self._crm_normalize_contact_type(payload.get('contact_type'))

        vals = {
            field_name: payload[field_name]
            for field_name in PARTNER_API_FIELDS
            if field_name in payload and payload[field_name] is not None
        }
        if contact_type is not None:
            vals['contact_type'] = contact_type
        for field_name in PARTNER_API_BOOL_FIELDS:
            if field_name in payload:
                vals[field_name] = bool(payload[field_name])

        # Resolve ISO country code (e.g. "AE") to res.country
        if payload.get('country_code'):
            vals['country_id'] = self._crm_resolve_country(payload['country_code'])

        # State requires country_code in the same request (or already in vals)
        if payload.get('state_name') or payload.get('state_code'):
            vals['state_id'] = self._crm_resolve_state(
                vals.get('country_id'),
                state_name=payload.get('state_name'),
                state_code=payload.get('state_code'),
            )

        return vals

    # -------------------------------------------------------------------------
    # API response & guards
    # -------------------------------------------------------------------------

    def _crm_api_serialize(self):
        """Format partner record for JSON API response."""
        self.ensure_one()
        # contact_code is the active ID for the current type (CUST/VEND/EMP)
        id_field = self._contact_id_field(self.contact_type) if self.contact_type else False
        return {
            'id': self.id,
            'name': self.name,
            'contact_type': self.contact_type,
            'contact_code': self[id_field] if id_field else False,
            'customer_id': self.customer_id,
            'vendor_id': self.vendor_id,
            'employee_id': self.employee_id,
            'email': self.email,
            'phone': self.phone,
            'mobile': self.mobile,
            'street': self.street,
            'street2': self.street2,
            'city': self.city,
            'zip': self.zip,
            'state_id': self.state_id.id or False,
            'state_name': self.state_id.name or False,
            'country_id': self.country_id.id or False,
            'country_code': self.country_id.code or False,
            'vat': self.vat,
            'is_company': self.is_company,
            'company_name': self.company_name,
            'ref': self.ref,
            'website': self.website,
            'active': self.active,
        }

    def _crm_api_check_writable(self):
        """Block updates to internal company partners and system users."""
        self.ensure_one()
        if self.is_internal_company or self.id in self._protected_partner_ids():
            raise AccessError('This contact cannot be updated through the CRM API.')

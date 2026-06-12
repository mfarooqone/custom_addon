from odoo import api, models
from odoo.exceptions import AccessError, ValidationError
from odoo.orm.types import DomainType

# Allowed values for contact_type (from custom_contacts module)
CONTACT_TYPES = frozenset({'customer', 'vendor', 'employee'})

# Partner fields accepted directly from JSON (no extra lookup)
PARTNER_API_FIELDS = (
    'name', 'email', 'phone', 'mobile', 'street', 'street2', 'city', 'zip',
    'vat', 'website', 'comment', 'ref', 'company_name',
)

CRM_API_RESPONSE_FIELDS = (
    'name', 'contact_type', 'customer_id', 'vendor_id', 'employee_id',
    'email', 'phone', 'mobile', 'street', 'street2', 'city', 'zip',
    'state_id', 'country_id', 'vat', 'is_company', 'company_name',
    'ref', 'website', 'active',
)


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit: list[str] | None = ['res.partner']

    # -------------------------------------------------------------------------
    # Authentication & request parsing
    # -------------------------------------------------------------------------

    @api.model
    def _crm_authenticate_company(self, request):
        """Validate API key and return the matching company.

        Key can be sent as:
        - Header: X-CRM-API-Key
        - Header: Authorization: Bearer <key>

        Integration must be enabled on the company (Settings -> CRM Integration).
        """
        api_key = request.httprequest.headers.get('X-CRM-API-Key', '').strip()
        if not api_key:
            authorization = request.httprequest.headers.get('Authorization', '')
            if authorization.startswith('Bearer '):
                api_key = authorization[7:].strip()
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
    def _crm_prepare_partner_vals(self, payload, *, for_create=False):
        """Build res.partner write/create values from API JSON.

        On create: name and contact_type are required.
        country_code / state_name / state_code are resolved to Odoo IDs.
        """
        if for_create:
            if not payload.get('name'):
                raise ValidationError('name is required.')
            if not payload.get('contact_type'):
                raise ValidationError('contact_type is required.')

        contact_type = payload.get('contact_type')
        if contact_type is not None:
            contact_type = str(contact_type).lower()
            if contact_type not in CONTACT_TYPES:
                raise ValidationError('contact_type must be one of: customer, vendor, employee.')

        vals = {
            field_name: payload[field_name]
            for field_name in PARTNER_API_FIELDS
            if field_name in payload and payload[field_name] is not None
        }
        if contact_type is not None:
            vals['contact_type'] = contact_type
        for field_name in ('is_company', 'active'):
            if field_name in payload:
                vals[field_name] = bool(payload[field_name])

        # Resolve ISO country code (e.g. "AE") to res.country
        country_code = payload.get('country_code')
        if country_code:
            country = self.env['res.country'].sudo().search([
                ('code', '=', str(country_code).upper()),
            ], limit=1)
            if not country:
                raise ValidationError(f'Unknown country code: {country_code}')
            vals['country_id'] = country.id

        # State requires country_code in the same request (or already in vals)
        state_name = payload.get('state_name')
        state_code = payload.get('state_code')
        if state_name or state_code:
            if not vals.get('country_id'):
                raise ValidationError('country_code is required when sending state_name or state_code.')
            domain: DomainType = [('country_id', '=', vals['country_id'])]
            domain = [
                *domain,
                ('code', '=', str(state_code).upper()) if state_code else ('name', '=ilike', state_name),
            ]
            state = self.env['res.country.state'].sudo().search(domain, limit=1)
            if not state:
                raise ValidationError('Unknown state for the given country.')
            vals['state_id'] = state.id

        return vals

    # -------------------------------------------------------------------------
    # API response & guards
    # -------------------------------------------------------------------------

    def _crm_api_serialize(self):
        """Format partner record for JSON API response."""
        self.ensure_one()
        fields_to_read = [name for name in CRM_API_RESPONSE_FIELDS if name in self._fields]
        row = self.read(fields_to_read)[0]
        contact_type = row.get('contact_type')
        # contact_code is the active ID for the current type (CUST/VEND/EMP)
        id_field = self._contact_id_field(contact_type) if contact_type else False
        state = row.get('state_id') or False
        country = row.get('country_id') or False
        return {
            'id': row['id'],
            'name': row['name'],
            'contact_type': contact_type,
            'contact_code': row.get(id_field) if id_field else False,
            'customer_id': row.get('customer_id'),
            'vendor_id': row.get('vendor_id'),
            'employee_id': row.get('employee_id'),
            'email': row.get('email'),
            'phone': row.get('phone'),
            'mobile': row.get('mobile'),
            'street': row.get('street'),
            'street2': row.get('street2'),
            'city': row.get('city'),
            'zip': row.get('zip'),
            'state_id': state[0] if state else False,
            'state_name': state[1] if state else False,
            'country_id': country[0] if country else False,
            'country_code': self.env['res.country'].browse(country[0]).code if country else False,
            'vat': row.get('vat'),
            'is_company': row.get('is_company'),
            'company_name': row.get('company_name'),
            'ref': row.get('ref'),
            'website': row.get('website'),
            'active': row.get('active'),
        }

    def _crm_api_check_writable(self):
        """Block updates to internal company partners and system users."""
        self.ensure_one()
        if self.is_internal_company or self.id in self._protected_partner_ids():
            raise AccessError('This contact cannot be updated through the CRM API.')

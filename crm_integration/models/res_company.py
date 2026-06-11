from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_crm_integration_enabled = fields.Boolean(
        string='Enable CRM Integration',
        default=False,
    )
    crm_api_key = fields.Char(
        string='CRM API Key',
        help='API key used to authenticate CRM requests.',
    )

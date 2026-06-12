from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Expose company fields on Settings -> CRM Integration
    enable_crm_integration = fields.Boolean(
        related='company_id.is_crm_integration_enabled',
        readonly=False,
    )
    crm_api_key = fields.Char(
        related='company_id.crm_api_key',
        readonly=False,
    )

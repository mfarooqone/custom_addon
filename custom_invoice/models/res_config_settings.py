from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_custom_invoice = fields.Boolean(
        related='company_id.is_invoice_customization_enabled',
        readonly=False,
    )

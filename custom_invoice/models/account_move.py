from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_name_invoice_report(self):
        self.ensure_one()
        if self.company_id.is_invoice_customization_enabled:
            return 'custom_invoice.report_invoice_document'
        return super()._get_name_invoice_report()

    use_custom_invoice_layout = fields.Boolean(compute='_compute_use_custom_invoice_layout')

    @api.depends('company_id.is_invoice_customization_enabled')
    def _compute_use_custom_invoice_layout(self):
        for move in self:
            move.use_custom_invoice_layout = move.company_id.is_invoice_customization_enabled

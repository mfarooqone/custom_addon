from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    partner_id = fields.Many2one(domain="[('contact_type', '=', 'vendor'), ('is_internal_company', '=', False)]")
    vendor_id = fields.Char(related='partner_id.vendor_id', string='Vendor ID', readonly=True)

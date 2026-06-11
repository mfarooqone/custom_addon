from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    partner_id = fields.Many2one(domain="[('contact_type', '=', 'customer'), ('is_internal_company', '=', False)]")
    customer_id = fields.Char(related='partner_id.customer_id', string='Customer ID', readonly=True)

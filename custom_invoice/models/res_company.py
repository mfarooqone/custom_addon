# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    is_invoice_customization_enabled = fields.Boolean(
        string='Activate Invoice Customization',
        default=False,
    )

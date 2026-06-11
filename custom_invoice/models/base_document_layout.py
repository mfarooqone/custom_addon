# -*- coding: utf-8 -*-
from odoo import api, fields, models


class BaseDocumentLayout(models.TransientModel):
    _inherit = 'base.document.layout'

    is_invoice_customization_enabled = fields.Boolean(
        related='company_id.is_invoice_customization_enabled',
    )

    @api.depends('is_invoice_customization_enabled')
    def _compute_preview(self):
        super()._compute_preview()

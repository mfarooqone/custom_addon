# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def color_scheme(self):
        if request and request.httprequest.cookies.get("color_scheme") == "dark":
            return "dark"
        return super().color_scheme()

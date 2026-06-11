from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sr_no = fields.Integer(string='Sr.', compute='_compute_sr_no')

    plate_no = fields.Char(string='Plate No')
    chassis_no = fields.Char(string='Chassis No')
    car_model = fields.Char(string='Car Model')
    service_start_date = fields.Date(string='Service Start Date')
    service_end_date = fields.Date(string='Service End Date')

    @api.model
    def _is_invoice_product_line(self, line):
        """Product lines use display_type 'product' or False before it is computed."""
        return not line.display_type or line.display_type == 'product'

    def _recompute_sr_no_for_moves(self, moves):
        for move in moves:
            product_lines = move.invoice_line_ids.filtered(
                self._is_invoice_product_line
            ).sorted(key=lambda line: (line.sequence, line.id or 0))
            for index, line in enumerate(product_lines, start=1):
                line.sr_no = index
            for line in move.invoice_line_ids - product_lines:
                line.sr_no = 0

    @api.depends(
        'sequence',
        'display_type',
        'move_id.invoice_line_ids',
        'move_id.invoice_line_ids.sequence',
        'move_id.invoice_line_ids.display_type',
    )
    def _compute_sr_no(self):
        for line in self:
            line.sr_no = 0
        self._recompute_sr_no_for_moves(self.mapped('move_id'))

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines._recompute_sr_no_for_moves(lines.move_id)
        return lines

    def write(self, vals):
        moves_before = self.move_id
        res = super().write(vals)
        if {'sequence', 'display_type', 'move_id'} & set(vals.keys()):
            self._recompute_sr_no_for_moves(self.move_id | moves_before)
        return res

    def unlink(self):
        moves = self.move_id
        res = super().unlink()
        self._recompute_sr_no_for_moves(moves)
        return res

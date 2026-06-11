from odoo import _, fields, models
from odoo.exceptions import UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    employee_code = fields.Char(
        string='Employee ID',
        related='work_contact_id.employee_id',
        readonly=True,
    )

    def _create_work_contacts(self):
        if any(employee.work_contact_id for employee in self):
            raise UserError(_('Some employee already have a work contact'))

        work_contacts = self.env['res.partner'].create([{
            'email': employee.work_email,
            'phone': employee.work_phone,
            'name': employee.name,
            'image_1920': employee.image_1920,
            'company_id': employee.company_id.id,
            'contact_type': 'employee',
        } for employee in self])

        for employee, work_contact in zip(self, work_contacts):
            employee.work_contact_id = work_contact

from odoo import api, models, fields


class CollegeStudents(models.Model):
    _name = 'college.students'
    _description = 'College student details'

    PROGRAM_SELECTION = [
        ('computer_science', 'Computer Science'),
        ('information_technology', 'Information Technology'),
        ('software_engineering', 'Software Engineering'),
        ('business_administration', 'Business Administration'),
        ('electrical_engineering', 'Electrical Engineering'),
    ]

    SEMESTER_SELECTION = [
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
    ]

    GUARDIAN_RELATION_SELECTION = [
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('guardian', 'Guardian'),
        ('other', 'Other'),
    ]

    _COMM_ADDRESS_FIELDS = [
        'comm_street', 'comm_street2', 'comm_city', 'comm_state_id', 'comm_zip', 'comm_country_id',
    ]
    _PERM_ADDRESS_FIELDS = [
        'perm_street', 'perm_street2', 'perm_city', 'perm_state_id', 'perm_zip', 'perm_country_id',
    ]

    image_1920 = fields.Image(string='Photo', max_width=1920, max_height=1920)
    image_128 = fields.Image(string='Photo (128)', related='image_1920', max_width=128, max_height=128, store=True)
    name = fields.Char(string='Name', required=True)
    age = fields.Integer(string='Age')
    gender = fields.Selection(string='Gender', selection=[('male', 'Male'), ('female', 'Female')])
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')

    comm_street = fields.Char(string='Communication Street')
    comm_street2 = fields.Char(string='Communication Street 2')
    comm_city = fields.Char(string='Communication City')
    comm_country_id = fields.Many2one('res.country', string='Communication Country')
    comm_state_id = fields.Many2one(
        'res.country.state',
        string='Communication State',
        domain="[('country_id', '=?', comm_country_id)]",
    )
    comm_zip = fields.Char(string='Communication ZIP')

    perm_street = fields.Char(string='Permanent Street')
    perm_street2 = fields.Char(string='Permanent Street 2')
    perm_city = fields.Char(string='Permanent City')
    perm_country_id = fields.Many2one('res.country', string='Permanent Country')
    perm_state_id = fields.Many2one(
        'res.country.state',
        string='Permanent State',
        domain="[('country_id', '=?', perm_country_id)]",
    )
    perm_zip = fields.Char(string='Permanent ZIP')

    same_as_communication = fields.Boolean(
        string='Permanent address same as communication address',
        default=True,
    )

    admission_number = fields.Char(string='Admission Number', required=True)
    admission_date = fields.Date(string='Admission Date', required=True)
    program = fields.Selection(
        string='Program',
        selection=PROGRAM_SELECTION,
    )
    batch = fields.Char(string='Batch')
    semester = fields.Selection(
        string='Semester',
        selection=SEMESTER_SELECTION,
    )
    guardian_name = fields.Char(string='Guardian Name')
    guardian_relation = fields.Selection(
        string='Relation',
        selection=GUARDIAN_RELATION_SELECTION,
    )
    guardian_phone = fields.Char(string='Guardian Phone')
    guardian_email = fields.Char(string='Guardian Email')
    notes = fields.Text(string='Internal Notes')

    def _get_address_values(self, prefix):
        self.ensure_one()
        return {
            f'{prefix}_street': getattr(self, f'{prefix}_street'),
            f'{prefix}_street2': getattr(self, f'{prefix}_street2'),
            f'{prefix}_city': getattr(self, f'{prefix}_city'),
            f'{prefix}_state_id': getattr(self, f'{prefix}_state_id').id if getattr(self, f'{prefix}_state_id') else False,
            f'{prefix}_zip': getattr(self, f'{prefix}_zip'),
            f'{prefix}_country_id': getattr(self, f'{prefix}_country_id').id if getattr(self, f'{prefix}_country_id') else False,
        }

    def _sync_permanent_from_communication(self):
        for student in self.filtered('same_as_communication'):
            comm_vals = student._get_address_values('comm')
            perm_vals = {
                perm_field: comm_vals[comm_field]
                for comm_field, perm_field in zip(self._COMM_ADDRESS_FIELDS, self._PERM_ADDRESS_FIELDS)
            }
            if any(student[f] != perm_vals[f] for f in self._PERM_ADDRESS_FIELDS):
                super(CollegeStudents, student).write(perm_vals)

    @api.onchange('comm_country_id')
    def _onchange_comm_country_id(self):
        if self.comm_country_id and self.comm_state_id.country_id != self.comm_country_id:
            self.comm_state_id = False

    @api.onchange('comm_state_id')
    def _onchange_comm_state_id(self):
        if self.comm_state_id.country_id and self.comm_country_id != self.comm_state_id.country_id:
            self.comm_country_id = self.comm_state_id.country_id

    @api.onchange('perm_country_id')
    def _onchange_perm_country_id(self):
        if self.perm_country_id and self.perm_state_id.country_id != self.perm_country_id:
            self.perm_state_id = False

    @api.onchange('perm_state_id')
    def _onchange_perm_state_id(self):
        if self.perm_state_id.country_id and self.perm_country_id != self.perm_state_id.country_id:
            self.perm_country_id = self.perm_state_id.country_id

    @api.onchange(
        'same_as_communication',
        'comm_street', 'comm_street2', 'comm_city', 'comm_state_id', 'comm_zip', 'comm_country_id',
    )
    def _onchange_same_as_communication(self):
        if not self.same_as_communication:
            return
        self.perm_street = self.comm_street
        self.perm_street2 = self.comm_street2
        self.perm_city = self.comm_city
        self.perm_state_id = self.comm_state_id
        self.perm_zip = self.comm_zip
        self.perm_country_id = self.comm_country_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('same_as_communication'):
                for comm_field, perm_field in zip(self._COMM_ADDRESS_FIELDS, self._PERM_ADDRESS_FIELDS):
                    vals.setdefault(perm_field, vals.get(comm_field))
        students = super().create(vals_list)
        students._sync_permanent_from_communication()
        return students

    def write(self, vals):
        res = super().write(vals)
        if vals.get('same_as_communication') or any(field in vals for field in self._COMM_ADDRESS_FIELDS):
            self._sync_permanent_from_communication()
        return res

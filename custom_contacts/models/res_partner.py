from odoo import api, fields, models


class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner', 'custom.contacts.contact.id.mixin']

    _customer_id_unique = models.Constraint('UNIQUE (customer_id)', 'Customer ID must be unique.')
    _vendor_id_unique = models.Constraint('UNIQUE (vendor_id)', 'Vendor ID must be unique.')
    _employee_id_unique = models.Constraint('UNIQUE (employee_id)', 'Employee ID must be unique.')

    contact_type = fields.Selection([
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('employee', 'Employee'),
    ], string='Contact Type')

    customer_id = fields.Char(string='Customer ID', readonly=True, copy=False)
    vendor_id = fields.Char(string='Vendor ID', readonly=True, copy=False)
    employee_id = fields.Char(string='Employee ID', readonly=True, copy=False)
    contact_code = fields.Char(string='ID', compute='_compute_contact_code')
    is_internal_company = fields.Boolean(string='Internal Company', readonly=True)

    @api.model
    def _company_partner_ids(self):
        return set(self.env['res.company'].sudo().search([]).mapped('partner_id').ids)

    @api.model
    def _user_partner_ids(self):
        return set(self.env['res.users'].sudo().search([]).mapped('partner_id').ids)

    @api.model
    def _protected_partner_ids(self):
        """Company and system user partners — never get contact type or sequential IDs."""
        return self._company_partner_ids() | self._user_partner_ids()

    def _clear_contact_id_fields(self):
        super(ResPartner, self).write({
            'contact_type': False,
            'customer_id': False,
            'vendor_id': False,
            'employee_id': False,
        })

    @api.depends('contact_type', 'customer_id', 'vendor_id', 'employee_id')
    def _compute_contact_code(self):
        for partner in self:
            field = self._contact_id_field(partner.contact_type)
            partner.contact_code = partner[field] if field else False

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        if 'contact_type' not in fields_list:
            return values
        mode = self.env.context.get('res_partner_search_mode')
        if mode == 'customer':
            values['contact_type'] = 'customer'
        elif mode == 'supplier':
            values['contact_type'] = 'vendor'
        elif self.env.context.get('default_contact_type') == 'employee':
            values['contact_type'] = 'employee'
        return values

    @api.model_create_multi
    def create(self, vals_list):
        partners = super().create(vals_list)
        protected_ids = self._protected_partner_ids()
        company_ids = self._company_partner_ids()
        for partner in partners:
            if partner.id in company_ids:
                partner.write({'is_internal_company': True})
            if partner.id in protected_ids:
                partner._clear_contact_id_fields()
                continue
            field = self._contact_id_field(partner.contact_type)
            if field and not partner[field]:
                partner[field] = self._next_contact_id(partner.contact_type)
        return partners

    def write(self, vals):
        res = super().write(vals)
        protected = self.filtered(lambda p: p.id in self._protected_partner_ids())
        if protected:
            protected._clear_contact_id_fields()
        for partner in self - protected:
            if partner.is_internal_company:
                continue
            if 'contact_type' in vals:
                field = self._contact_id_field(partner.contact_type)
                if field and not partner[field]:
                    partner[field] = self._next_contact_id(partner.contact_type)
        return res

    @api.model
    def _restore_missing_contact_types(self, skip_ids):
        """Re-assign contact_type after module reinstall wiped custom fields."""
        Partner = self.with_context(active_test=False)
        Partner.search([
            ('id', 'not in', skip_ids),
            ('contact_type', '=', 'employee'),
            ('customer_rank', '>', 0),
        ]).write({'contact_type': 'customer', 'employee_id': False})
        Partner.search([
            ('id', 'not in', skip_ids),
            ('contact_type', '=', 'employee'),
            ('supplier_rank', '>', 0),
        ]).write({'contact_type': 'vendor', 'employee_id': False})

        untyped = Partner.search([
            ('id', 'not in', skip_ids),
            ('is_internal_company', '=', False),
            '|', ('contact_type', '=', False), ('contact_type', '=', ''),
        ])

        if 'purchase.order' in self.env:
            vendor_partners = self.env['purchase.order'].sudo().search([]).mapped(
                'partner_id.commercial_partner_id'
            )
            (untyped & vendor_partners).write({'contact_type': 'vendor'})
            untyped -= vendor_partners

        if 'sale.order' in self.env:
            customer_partners = self.env['sale.order'].sudo().search([]).mapped(
                'partner_id.commercial_partner_id'
            )
            (untyped & customer_partners).write({'contact_type': 'customer'})
            untyped -= customer_partners

        if 'account.move' in self.env:
            invoice_customers = self.env['account.move'].sudo().search([
                ('move_type', 'in', ('out_invoice', 'out_refund')),
            ]).mapped('partner_id.commercial_partner_id')
            (untyped & invoice_customers).write({'contact_type': 'customer'})
            untyped -= invoice_customers

            invoice_vendors = self.env['account.move'].sudo().search([
                ('move_type', 'in', ('in_invoice', 'in_refund')),
            ]).mapped('partner_id.commercial_partner_id')
            (untyped & invoice_vendors).write({'contact_type': 'vendor'})
            untyped -= invoice_vendors

        untyped.filtered(
            lambda partner: partner.supplier_rank > 0
            and (partner.customer_rank == 0 or partner.supplier_rank > partner.customer_rank)
        ).write({'contact_type': 'vendor'})
        untyped = untyped.filtered(lambda partner: not partner.contact_type)

        untyped.filtered(lambda partner: partner.customer_rank > 0).write({
            'contact_type': 'customer',
        })
        untyped = untyped.filtered(lambda partner: not partner.contact_type)

        untyped.filtered(lambda partner: partner.supplier_rank > 0).write({
            'contact_type': 'vendor',
        })
        untyped = untyped.filtered(lambda partner: not partner.contact_type)

        if 'hr.employee' in self.env:
            employees = self.env['hr.employee'].sudo().search([])
            employee_partners = employees.mapped('work_contact_id').filtered(
                lambda partner: partner
                and partner.id not in skip_ids
                and partner.customer_rank == 0
                and partner.supplier_rank == 0
            )
            (untyped & employee_partners).write({'contact_type': 'employee'})
            untyped -= employee_partners

            for employee in employees.filtered(lambda emp: not emp.work_contact_id):
                partner = untyped.filtered(lambda p, emp=employee: p.name == emp.name)[:1]
                if partner:
                    partner.write({'contact_type': 'employee'})
                    untyped -= partner

    @api.model
    def _sync_all_contact_sequences(self):
        """Called on module upgrade — fix internal company partner, backfill IDs, sync counters."""
        protected_ids = list(self._protected_partner_ids()) or [0]
        company_ids = list(self._company_partner_ids())
        skip_ids = protected_ids

        if company_ids:
            self.browse(company_ids).write({'is_internal_company': True})
        if protected_ids:
            self.browse(protected_ids)._clear_contact_id_fields()

        self.with_context(active_test=False).search([
            ('contact_type', '=', 'company'),
            ('id', 'not in', skip_ids),
        ]).write({'contact_type': 'customer'})
        self.search([
            ('is_internal_company', '=', True),
            ('id', 'not in', company_ids or [0]),
        ]).write({'is_internal_company': False})

        self._restore_missing_contact_types(skip_ids)

        for contact_type, field_name in (
            ('customer', 'customer_id'),
            ('vendor', 'vendor_id'),
            ('employee', 'employee_id'),
        ):
            missing = self.search([
                ('contact_type', '=', contact_type),
                ('id', 'not in', skip_ids),
                '|', (field_name, '=', False), (field_name, '=', ''),
            ])
            for partner in missing:
                partner[field_name] = self._next_contact_id(contact_type)

        return super()._sync_all_contact_sequences()

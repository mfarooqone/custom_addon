from collections import defaultdict

from odoo import api, models

# Each contact type: sequence code, field on partner, and ID prefix
CONTACT_SEQUENCES = {
    'customer': ('customer.id', 'customer_id', 'CUST/'),
    'vendor': ('vendor.id', 'vendor_id', 'VEND/'),
    'employee': ('employee.id', 'employee_id', 'EMP/'),
}


class ContactIdMixin(models.AbstractModel):
    _name = 'custom.contacts.contact.id.mixin'
    _description = 'Auto contact ID helpers'

    @api.model
    def _contact_id_field(self, contact_type):
        return CONTACT_SEQUENCES.get(contact_type, (None, None, None))[1]

    @api.model
    def _highest_stored_number(self, field_name, prefix):
        numbers = []
        for value in self.search([(field_name, 'like', prefix + '%')]).mapped(field_name):
            try:
                numbers.append(int(value.removeprefix(prefix)))
            except ValueError:
                pass
        return max(numbers, default=0)

    @api.model
    def _bump_sequence(self, sequence_code, field_name, prefix):
        sequence = self.env['ir.sequence'].search([('code', '=', sequence_code)], limit=1)
        if not sequence:
            return
        required = self._highest_stored_number(field_name, prefix) + 1
        if sequence.number_next < required:
            sequence.number_next = required

    @api.model
    def _fix_duplicate_ids(self, contact_type):
        sequence_code, field_name, prefix = CONTACT_SEQUENCES[contact_type]
        groups = defaultdict(list)
        for partner in self.search([(field_name, 'like', prefix + '%')], order='id'):
            groups[partner[field_name]].append(partner)
        for partners in groups.values():
            if len(partners) <= 1:
                continue
            self._bump_sequence(sequence_code, field_name, prefix)
            for partner in partners[1:]:
                partner[field_name] = self.env['ir.sequence'].next_by_code(sequence_code)

    @api.model
    def _sync_all_contact_sequences(self):
        """Fix duplicate IDs and align sequence counters."""
        for contact_type, (code, field, prefix) in CONTACT_SEQUENCES.items():
            self._fix_duplicate_ids(contact_type)
            self._bump_sequence(code, field, prefix)

    @api.model
    def _next_contact_id(self, contact_type):
        code, field_name, prefix = CONTACT_SEQUENCES[contact_type]
        self._bump_sequence(code, field_name, prefix)
        return self.env['ir.sequence'].next_by_code(code)

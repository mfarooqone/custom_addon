# Re-point xmlids from college_erp before data files load (avoids duplicates on split).
MOVED_XMLIDS = (
    'seq_customer',
    'seq_vendor',
    'seq_employee',
    'view_partner_kanban_inherit_contact_type',
    'view_partner_tree_inherit_contact_type',
    'view_partner_form_inherit_contact_type',
    'view_res_partner_filter_inherit_contact_type',
    'view_sale_order_tree_inherit_customer_id',
    'view_sale_order_kanban_inherit_customer_id',
    'view_purchase_order_tree_inherit_vendor_id',
    'view_purchase_order_kpis_tree_inherit_vendor_id',
    'view_purchase_order_kanban_inherit_vendor_id',
    'view_employee_form_inherit_employee_id',
    'view_employee_list_inherit_employee_code',
    'view_employee_kanban_inherit_employee_code',
)


def pre_init_hook(env):
    env.cr.execute(
        """
        UPDATE ir_model_data
           SET module = 'custom_contacts'
         WHERE module = 'college_erp'
           AND name = ANY(%s)
        """,
        (list(MOVED_XMLIDS),),
    )

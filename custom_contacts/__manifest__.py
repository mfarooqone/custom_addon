{
    'name': 'Custom Contacts',
    'version': '19.0.1.1.0',
    'license': 'LGPL-3',
    'author': 'Najoom Al Thuraya',
    'website': 'https://althurayauae.com/',
    'category': 'Sales/CRM',
    'summary': 'Typed contacts with auto-generated customer, vendor, and employee IDs',
    'description': """
        Contact type enforcement (customer / vendor / employee) with sequential IDs,
        partner views, and domain filters on sales, purchase, and HR.
    """,
    'depends': ['base', 'contacts', 'sale', 'purchase', 'hr', 'account'],
    'auto_install': True,
    'installable': True,
    'application': False,
    'sequence': -100,
    'icon': '/custom_contacts/static/description/icon.png',
    'pre_init_hook': 'pre_init_hook',
    'data': [
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
        'views/hr_employee_views.xml',
        'data/ir_sequence_data.xml',
        'data/ir_sequence_sync.xml',
    ],
}

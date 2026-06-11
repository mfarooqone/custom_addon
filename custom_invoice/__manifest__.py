{
    'name': 'Custom Invoice',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'Najoom Al Thuraya',
    'website': 'https://althurayauae.com/',
    'category': 'Accounting/Accounting',
    'summary': 'Custom invoice layout, fields, and PDF reports',
    'description': """
        Custom invoice PDF layout with header/footer, invoice line fields,
        and company-level toggle for custom invoice formatting.
    """,
    'depends': ['web', 'account', 'sale'],
    'auto_install': True,
    'installable': True,
    'application': False,
    'data': [
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
        'views/report_templates.xml',
        'views/report_invoice.xml',
        'views/account_move_views.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'custom_invoice/static/src/css/report_custom_invoice.css',
        ],
        'web.report_assets_pdf': [
            'custom_invoice/static/src/css/report_custom_invoice.css',
        ],
    },
}

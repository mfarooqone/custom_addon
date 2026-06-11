{
    'name': 'CRM Integration',
    'version': '19.0.1.0.1',
    'license': 'LGPL-3',
    'author': 'Najoom Al Thuraya',
    'website': 'https://althurayauae.com/',
    'category': 'Sales/CRM',
    'summary': 'Company-level CRM integration toggle and settings',
    'description': """
        CRM Integration module with a company-level setting to enable
        or disable CRM integration features.
    """,
    'depends': ['crm'],
    'installable': True,
    'application': False,
    'sequence': -85,
    'icon': '/crm_integration/static/description/icon.png',
    'data': [
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
    ],
}

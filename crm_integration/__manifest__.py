{
    'name': 'CRM Integration',
    'version': '19.0.1.4.0',
    'license': 'LGPL-3',
    'author': 'Najoom Al Thuraya',
    'website': 'https://althurayauae.com/',
    'category': 'Sales/CRM',
    'summary': 'CRM integration APIs and company-level settings',
    'description': (
        'CRM Integration module with REST APIs to create and update contacts, '
        'company-level API key authentication, and contact type support.'
    ),
    'depends': ['crm', 'custom_contacts'],
    'installable': True,
    'application': False,
    'sequence': -85,
    'icon': '/crm_integration/static/description/icon.png',
    'data': [
        'views/api_doc_action.xml',
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
    ],
}

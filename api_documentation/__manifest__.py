{
    'name': 'API Documentation',
    'version': '19.0.1.0.0',
    'license': 'LGPL-3',
    'author': 'Najoom Al Thuraya',
    'website': 'https://althurayauae.com/',
    'category': 'Technical',
    'summary': 'Shared REST API documentation page for custom integrations',
    'description': """
        Provides a common API documentation page that other custom modules
        can extend with their own endpoints and examples.
    """,
    'depends': ['base_setup'],
    'installable': True,
    'application': False,
    'sequence': -95,
    'icon': '/api_documentation/static/description/icon.png',
    'data': [
        'views/api_doc.xml',
        'views/res_config_settings_views.xml',
    ],
}

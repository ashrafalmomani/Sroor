# -*- encoding: utf-8 -*-
{
    'name': 'Login Background And Styles',
    'summary': 'The new configurable odoo web login screen',
    'version': '12.0.2.0.0',
    'category': 'website',
    'summary': """
    You can customised login page like add background image or color and change position of login form.
    """,
    'author': 'Fortutech IMS Pvt. Ltd.',
    'website': 'https://www.fortutechims.com',
    'license': 'AGPL-3',
    'depends': ['base', 'base_setup', 'web', 'web_widget_color', 'auth_signup'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/login_image.xml',
        'templates/left_login_template.xml',
        'templates/right_login_template.xml',
        'templates/middle_login_template.xml',
        'templates/assets.xml',
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'images': ['static/description/banner.png'],
}


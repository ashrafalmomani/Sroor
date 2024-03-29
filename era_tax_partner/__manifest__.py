# -*- coding: utf-8 -*-
{
    'name': "Electronic invoice KSA - Sales & Purchase | qrcode | ZATCA | vat | e-invoice | tax | Zakat",
    "version" : "12.0.0.4",
    "category" : "Accounting",
    'description': """
       Electronic invoice KSA - Sales & Purchase
    """,
    'author': "Era group",
    'email': "aqlan@era.net.sa ",
    'website': "https://era.net.sa",
    'category': 'accounting',
    'version': '0.1',
    'price': 0,  
    'currency': 'USD',
    'license': 'AGPL-3',
    'images': ['static/description/main_screenshot.png'],
    'depends': ['base', 'account', 'sale', 'purchase', 'account_cancel'],
    'data': [
        'security/security_group.xml',
        'views/partner.xml',
        'views/account_move.xml',
        'reports/invoice_inherit_report.xml',
    ],
}

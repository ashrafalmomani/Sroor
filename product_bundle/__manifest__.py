# -*- coding: utf-8 -*-
{
    "name": "Product Bundle Pack",
    "category": 'Sales',
    "summary": """Combine two or more products together in order to create a bundle product.""",
    "description": """
        BrowseInfo developed a new odoo/OpenERP module apps.
        This module is use to create Product Bundle,Product Pack, Bundle Pack of Product, Combined Product pack.
        -Product Pack, Custom Combo Product, Bundle Product. Customized product, Group product.Custom product bundle. Custom Product Pack.
        -Pack Price, Bundle price, Bundle Discount, Bundle Offer.
    """,
    "sequence": 1,
    "author": "Digital Assets",
    "website": "http://www.digitalais.com",
    "version": '0.1',
    "depends": ['sale', 'product', 'stock', 'sale_stock', 'sale_management'],
    "data": [
        'views/product_view.xml',
        'wizard/product_bundle_wizard_view.xml',
        'security/ir.model.access.csv'
    ],
    "installable": True,
    "application": True,

}

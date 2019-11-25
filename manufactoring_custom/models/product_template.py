# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    num_days = fields.Char(string='Number of Days')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    num_days = fields.Char(string='Number of Days')


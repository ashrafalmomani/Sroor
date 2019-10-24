# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Sales(models.Model):
    _inherit = "sale.order"

    doc_order_number = fields.Char(string='Doctor Order #')


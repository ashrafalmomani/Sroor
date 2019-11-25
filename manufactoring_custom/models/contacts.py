# -*- coding: utf-8 -*-

from odoo import fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    commercial_record = fields.Char(string='Commercial Record')
    is_doctor = fields.Selection([('doctor', 'Doctor '), ('not_doctor', ' Not Doctor')], default='not_doctor',)

# -*- coding: utf-8 -*-

from odoo import models, fields, _


class SectionDental(models.Model):
    _name = 'section'
    _description = 'section'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", required="1", translate=True)
    description = fields.Char(string="Description", track_visibility='onchange')
    first_section = fields.Boolean('IS First Section?', track_visibility='onchange')
    invoice_section = fields.Boolean('Invoice Section?', track_visibility='onchange')
    section_type = fields.Selection([('1', 'porcelain'), ('2', 'Cercon'), ('3', 'E-Max'), ('4', 'Wax-Meatl'),('5', 'Acrylic'), ('6', 'Gypsum'),('7', 'Controll and invoice')], track_visibility='onchange')

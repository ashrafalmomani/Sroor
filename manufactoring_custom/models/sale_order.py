# -*- coding: utf-8 -*-

from odoo import api, fields, models,_
from datetime import timedelta
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    model = fields.Boolean(string='Model')
    tryy = fields.Boolean(string='Try')
    bite = fields.Boolean(string='Bite')
    teeth = fields.Boolean(string='Teeth')
    photos = fields.Boolean(string='Photos')
    face_bow = fields.Boolean(string='Face Bow')
    mother_model = fields.Boolean(string='Mother Model')
    impression = fields.Boolean(string='Impression')
    usb = fields.Boolean(string='USB')
    other = fields.Boolean(string='Other')
    noteother = fields.Text(string='Note')
    doc_order_number = fields.Char(string='Doctor Order #')
    partner_id = fields.Many2one('res.partner', string='Doctor Name')
    partner_address_phone = fields.Char('Doctor Phone', related='partner_id.phone', readonly=True)
    patient_name = fields.Char(string='Patient Name')
    patient_age = fields.Char(string='Patient Age')
    num_file_patient = fields.Char(string='Number File patient')
    patient_phone = fields.Char(string='Patient Phone')
    status_order = fields.Selection([('urgent', 'Urgent'), ('not_urgent', ' Not Urgent')], default='not_urgent', required=1)
    customer_request_number = fields.Char(string='Customer Requset Number')

    @api.multi
    def action_confirm(self):
        super(SaleOrder, self).action_confirm()
        if not self.order_line:
            raise UserError(_('No lines found to create manufacturing order.'))
        dental_obj = self.env['dental']
        for line in self.order_line:
            dental_obj.create({'order_id': self.id,
                               'name': self.name,
                               'product_id': line.product_id.id,
                               'product_uom_qty': line.product_uom_qty,
                               'price_unit': line.price_unit,
                               'description': line.name,
                               'teeth_num': [(6, 0, line.teeth_num_ids.ids)],
                               'color_num': line.color_num,
                               'date_status': line.date_status,
                               'date_delivery': line.date_delivery,
                               'order_date': self.confirmation_date,
                               'partner_id': self.partner_id.id,
                               'discount': line.discount,
                               })

    @api.multi
    def manufacturing_orders(self):
        return {
            'name': _('Manufacturing Orders'),
            'view_type': 'form',
            'view_mode': 'tree',
            "views": [[False, "tree"], [False, "form"]],
            'res_model': 'dental',
            'view_id': self.env.ref('manufactoring_custom.dental_tree').id,
            'type': 'ir.actions.act_window',
            'domain': [['order_id', '=', self.id]],
            'context': {'default_order_id': self.id},
            'target': 'current',
        }


class SaleOrderLines(models.Model):
    _inherit = 'sale.order.line'

    date_status = fields.Date('Try In')
    date_delivery = fields.Date('Delivery Date')
    teeth_num_ids = fields.Many2many('teeth.num', string="Teeth Num")
    color_num = fields.Selection([('none', 'None'), ('0M1', '0M1'), ('0M2', '0M2'), ('0M3', '0M3'), ('1M1', '1M1'), ('1M2', '1M2'), ('1M3', '1M3'),('2M0', '2M0'), ('2M1', ' 2M1'), ('2M2', ' 2M2'), ('3M0', '3M0'), ('3M1', '3M1'), ('A1', 'A1'), ('A2', 'A2'), ('A3', 'A3'), ('A3.5', 'A3.5'),('A4', 'A4'), ('B1', 'B1'), ('B2', 'B2'), ('B3', 'B3'), ('B4', 'B4'), ('C1', 'C1'), ('C2', ' C2'), ('C3', 'C3'),('C4', 'C4'), ('D2', 'D2'), ('D3', 'D3'), ('D4', 'D4'), ('45', '45')], default='none', required=1)
    product_note = fields.Char('Note')
    num_days = fields.Char('number of day')

    @api.onchange('product_id')
    def product_id_onchange_value(self):
        if self.product_id:
            current_date = fields.Date.today()
            self.date_delivery = current_date + timedelta(days=int(self.product_id.num_days))


class TeethNum(models.Model):
    _name = 'teeth.num'
    _description = 'teeth number'

    name = fields.Char('Teeth number')


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    date_status = fields.Date('Try In')
    date_delivery = fields.Date('Delivery Date')
    teeth_num_ids = fields.Many2many('teeth.num', string="Teeth Num")
    color_num = fields.Selection([('none', 'None'), ('0M1', '0M1'), ('0M2', '0M2'), ('0M3', '0M3'), ('1M1', '1M1'), ('1M2', '1M2'), ('1M3', '1M3'),('2M0', '2M0'), ('2M1', ' 2M1'), ('2M2', ' 2M2'), ('3M0', '3M0'), ('3M1', '3M1'), ('A1', 'A1'), ('A2', 'A2'), ('A3', 'A3'), ('A3.5', 'A3.5'),('A4', 'A4'), ('B1', 'B1'), ('B2', 'B2'), ('B3', 'B3'), ('B4', 'B4'), ('C1', 'C1'), ('C2', ' C2'), ('C3', 'C3'),('C4', 'C4'), ('D2', 'D2'), ('D3', 'D3'), ('D4', 'D4'), ('45', '45')], default='none', required=1)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.depends('mo_ids')
    def check_has_mo_ids(self):
        if self.mo_ids:
            self.has_mo_ids = True

    doc_order_number = fields.Char(string='Doctor Order #')
    patient_name = fields.Char(string='Patient Name')
    patient_age = fields.Char(string='Patient Age')
    num_file_patient = fields.Char(string='Number File patient')
    patient_phone = fields.Char(string='Patient Phone')
    status_order = fields.Selection([('urgent', 'Urgent'), ('not_urgent', ' Not Urgent')], default='not_urgent', required=1)
    customer_request_number = fields.Char(string='Customer Requset Number')
    has_mo_ids = fields.Boolean(compute='check_has_mo_ids',default=False)

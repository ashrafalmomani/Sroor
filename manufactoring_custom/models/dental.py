# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo import models, fields, api, _


class ManufacturingDental(models.Model):
    _name = 'dental'
    _description = 'Dental'
    _rec_name = 'number'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_section_id(self):
        section_id = self.env['section'].search([]).filtered(lambda y: y.first_section)
        return section_id.id

    def _compute_total_amount(self):
        for rec in self:
            amount = rec.price_unit * rec.product_uom_qty
            rec.total_amount = amount - (amount * (rec.discount / 100))

    number = fields.Char("Number", copy=False, defualt='New')
    name = fields.Char(string="Sale Order #", track_visibility='onchange')
    description = fields.Char(string="Description", track_visibility='onchange')
    product_id = fields.Many2one('product.product', string='Product', track_visibility='onchange')
    product_uom_qty = fields.Float('Qty Ordered', track_visibility='onchange')
    price_unit = fields.Float('Unit Price', track_visibility='onchange')
    date_status = fields.Date('Try In', track_visibility='onchange')
    date_delivery = fields.Date('Delivery Date', track_visibility='onchange')
    teeth_num = fields.Many2many('teeth.num', string="Teeth Num")
    color_num = fields.Char(string="Color Name", track_visibility='onchange')
    order_id = fields.Many2one('sale.order', "Sale Order", )
    state = fields.Selection([('draft', 'draft'), ('in_progress', 'In Progress'),('to_invoice', 'To Invoice'),
                              ('invoice', 'Invoiced'), ('cancel', 'Cancel')], default='draft', track_visibility='onchange')
    current_section_id = fields.Many2one('section', "Current Section", default=_default_section_id, track_visibility='onchange')
    routing_id = fields.Many2one('mo.routing', "Routing")
    operation_ids = fields.One2many('mo.operations', "dental_id")
    section_date = fields.Date(string='Date')
    order_date = fields.Date(string=' Order Date')
    note = fields.Char('Note')
    send_by_email = fields.Boolean('Send Feedback Email')
    partner_id = fields.Many2one('res.partner', string='Customer')
    invoice_id = fields.Many2one('account.invoice', 'Invoice')
    inv_count = fields.Integer('# Invoices', compute='_compute_inv_count')
    discount = fields.Float('Discount', track_visibility='onchange')
    total_amount = fields.Float(compute='_compute_total_amount', string='Total Amount')

    @api.one
    def _compute_inv_count(self):
        inv = self.env['account.invoice'].search([('origin', '=', self.number)])
        self.inv_count = len(inv)

    @api.multi
    def action_invoice(self):
        """when click invoice create invoice and validate picking in sale order"""
        picking_ids = self.order_id.picking_ids
        if picking_ids.state != 'done':
            for picking_id in picking_ids:
                picking_id.action_confirm()
                picking_id.action_assign()
                for pack in picking_id.move_line_ids_without_package:
                    if pack.product_qty > 0:
                        pack.write({'qty_done': pack.product_qty})
                picking_id.button_validate()

        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        if not journal_id:
            raise UserError(_('Please define an accounting sales journal for this company.'))

        line_values = []
        invoice_obj = self.env['account.invoice']
        account = self.env['account.journal'].browse(journal_id).default_credit_account_id
        values = {
            'name': self.product_id.name,
            'origin': self.number,
            'type': 'out_invoice',
            'account_id': account.id,
            'price_unit': self.price_unit,
            'quantity': self.product_uom_qty,
            'uom_id': self.product_id.uom_id.id,
            'product_id': self.product_id.id or False,
            'invoice_line_tax_ids': [(6, 0, self.product_id.taxes_id.ids)],
            'date_status': self.date_status,
            'date_delivery': self.date_delivery,
            'color_num': self.color_num,
            'teeth_num_ids':  [(6, 0, self.teeth_num.ids)],
            'discount': self.discount,
        }
        line_values.append([0, False, values])

        invoice = invoice_obj.sudo().create({
            'name': '',
            'origin': self.name,
            'name': self.number,
            'type': 'out_invoice',
            'account_id': self.partner_id.property_account_receivable_id.id,
            'partner_id': self.partner_id.id,
            'partner_shipping_id': self.partner_id.id,
            'journal_id': journal_id,
            'payment_term_id': self.partner_id.property_payment_term_id.id or False,
            'company_id': self.env.user.company_id.id,
            'user_id': self.env.uid,
            'mo_ids': [(6, 0, [self.id])],
            'invoice_line_ids': line_values,
            'patient_name': self.order_id.patient_name,
            'patient_age': self.order_id.patient_age,
            'num_file_patient': self.order_id.num_file_patient,
            'patient_phone': self.order_id.patient_phone,
            'status_order': self.order_id.status_order,
            'customer_request_number': self.order_id.customer_request_number,
            'invoice_picking_id': picking_ids.id,
        })
        invoice.action_invoice_open()
        self.state = 'invoice'
        self.order_id.invoice_status = 'invoiced'

    @api.multi
    def action_cancel_so(self):
        self.order_id.action_cancel()
        mo_ids = self.env['dental'].search([('order_id', '=', self.order_id.id)])
        for rec in mo_ids:
            rec.state = 'cancel'

    @api.multi
    def action_return(self):
        invoice_id = self.env['account.invoice'].search([('mo_ids', 'in', self.id)], order="id desc", limit=1)
        if invoice_id.amount_total == invoice_id.residual:
            credit_note_wizard = self.env['account.invoice.refund'].with_context(
                {'active_ids': [invoice_id.id], 'active_id': invoice_id.id}).create({
                 'filter_refund': 'cancel',
                 'description': 'Modified Invoice'})
            credit_note_wizard.invoice_refund()
            for rec in invoice_id.mo_ids:
                rec.state = 'cancel'
        else:
            raise UserError(_('You cant return paid invoice'))

    @api.model
    def create(self, vals):
        number = self.env['ir.sequence'].next_by_code('dental') or '/'
        vals.update({'number': number})
        return super(ManufacturingDental, self).create(vals)

    @api.multi
    def confirm(self):
        operation_id = self.env['mo.operations'].create({'name': '1',
                                                         'section_from': self.order_id.name,
                                                         'section_to': self.current_section_id.name,
                                                         'note': self.note,
                                                         })
        self.operation_ids = operation_id.ids and [(6, 0, operation_id.ids)] or False
        self.state = 'in_progress'

    @api.model
    def action_invoice_mo_orders(self):
        order_ids = self.env['dental'].search([('current_section_id.invoice_section', '=', True)])
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree',
            "views": [[False, "tree"], [False, "form"]],
            'view_id': self.env.ref('manufactoring_custom.dental_tree').id,
            'type': 'ir.actions.act_window',
            'name': 'Invoice Orders',
            'res_model': 'dental',
            'domain': [('id', 'in', order_ids.ids)],
            'target': 'self',
        }

    @api.multi
    def transfer(self, data):
        data['form'] = {}
        return {
            'name': _('Section wizard'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'section.wizard',
            'view_id': self.env.ref('manufactoring_custom.view_section_wizard').id,
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.multi
    def sale_orders(self):
        return {
            'name': _('Sale Orders'),
            'view_type': 'form',
            'view_mode': 'tree',
            "views": [[False, "tree"], [False, "form"]],
            'res_model': 'sale.order',
            'view_id': self.env.ref('sale.view_order_tree').id,
            'type': 'ir.actions.act_window',
            "domain": [['name', '=', self.order_id.name]],
            'context': {'default_order_id': self.id},
            'target': 'current',
        }


class MOOperations(models.Model):
    _name = 'mo.operations'
    _description = 'Operations'

    section_from = fields.Char(string="Section From")
    section_to = fields.Char(string="Section to")
    note = fields.Char('Note')
    date = fields.Datetime(string="Date", default=fields.Datetime.now, readonly=True)
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self._uid)
    dental_id = fields.Many2one('dental')
    name = fields.Char("Name")


class SectionWizard(models.TransientModel):
    _name = 'section.wizard'

    @api.model
    def _get_default_manager(self):
        return self.env['res.users'].search([('groups_id', 'in', self.env.ref('hr.group_hr_manager').id)], limit=1, order="id desc")

    section_id = fields.Many2one('section', "Section", requried=1)
    note = fields.Text('Note')
    invoice_section = fields.Boolean(related='section_id.invoice_section')
    manager = fields.Many2one('res.users', string='Manager', default=_get_default_manager)
    check_quality_transfer = fields.Selection([('invoice', 'Invoice'), ('try_in', 'Try In'),
                                               ('return', 'Return'), ('cancel', 'Cancel')], track_visibility='onchange')

    def confirm_transfer(self):
        active_id = self._context.get('active_id')
        dental_id = self.env['dental'].browse(active_id)
        current_section = dental_id.current_section_id
        if current_section == self.section_id:
            raise UserError(_('Please define an Another section'))

        if self.check_quality_transfer:
            dental_id.state = 'to_invoice'

        if self.check_quality_transfer in ('return', 'cancel'):
            note = '( ' + self.check_quality_transfer + ' )' + self.note
        else:
            note = self.note
        operation_id = self.env['mo.operations'].create({'section_to': self.section_id.name,
                                                         'section_from': dental_id.current_section_id.name,
                                                         'note': note,
                                                         })

        dental_id.operation_ids = operation_id and [(4, operation_id.id)] or False
        dental_id.current_section_id = self.section_id.id
        user_id = self.env['res.users'].search([('groups_id', '=', self.env.ref('manufactoring_custom.manufacturing_group_manager').id)], limit=1, order="id desc")
        self.env['mail.activity'].create({
            'res_id': self.id,
            'res_model_id': self.env['ir.model'].search([('model', '=', 'dental')], limit=1).id,
            'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
            'summary': 'Test',
            'note': 'test  %s',
            'user_id': user_id.id,
        })
        template_id = self.env.ref('manufactoring_custom.send_email')
        composer = self.env['mail.compose.message'].sudo().with_context({
            'default_composition_mode': 'mass_mail',
            'default_notify': False,
            'default_model': 'section.wizard',
            'default_res_id': self.id,
            'default_template_id': template_id.id,
        }).create({})
        values = composer.onchange_template_id(template_id.id, 'mass_mail', 'section.wizard', self.id)['value']
        composer.write(values)
        composer.send_mail()

        if int(current_section.section_type) == 1:
            section_menu = 'manufactoring_custom.menu_manufacturing_orders_porcelain'
        if int(current_section.section_type) == 2:
            section_menu = 'manufactoring_custom.menu_manufacturing_orders_cercon'
        if int(current_section.section_type) == 3:
            section_menu = 'manufactoring_custom.menu_manufacturing_orders_e-max'
        if int(current_section.section_type) == 4:
            section_menu = 'manufactoring_custom.menu_manufacturing_orders_wax-metal'
        if int(current_section.section_type) == 5:
            section_menu = 'manufactoring_custom.menu_manufacturing_orders_acrylic'
        if int(current_section.section_type) == 6:
            section_menu = 'manufactoring_custom.menu_manufacturing_orders_gypsum'
        if int(current_section.section_type) == 7:
            section_menu = 'manufactoring_custom.menu_inv_manufacturing_orders'

        return {
            'type': 'ir.actions.client',
            'name': 'Orders',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref(section_menu).id},
        }


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    mo_ids = fields.Many2many('dental', 'dental_invoice_rel', 'dental_id', 'invoice_id', "Manufacturing orders")


class InvoiceWizard(models.TransientModel):
    _name = 'invoice.wizard'

    @api.multi
    def action_invoice(self):
        dental_ids = self.env['dental'].browse(self._context.get('active_ids'))
        partner_list = []
        line_values = []
        mo_list_ids = []
        order_list = []

        for rec in dental_ids:
            order_list.append(rec.order_id.id)
            partner_list.append(rec.partner_id.id)
            partner = rec.partner_id

        if len(list(set(partner_list))) != 1:
            raise UserError(_('You cant confirm multi order for different customer'))

        if len(list(set(order_list))) != 1:
            raise UserError(_('You cant confirm multi order for different sale order'))

        journal_id = self.env['account.invoice'].default_get(['journal_id'])['journal_id']
        account = self.env['account.journal'].browse(journal_id).default_credit_account_id
        for rec in dental_ids:
            if rec.state == 'to_invoice':
                values = {
                    'name': rec.product_id.name,
                    'origin': rec.number,
                    'account_id': account.id,
                    'price_unit': rec.price_unit,
                    'quantity': rec.product_uom_qty,
                    'uom_id': rec.product_id.uom_id.id,
                    'product_id': rec.product_id.id or False,
                    'invoice_line_tax_ids': [(6, 0, rec.product_id.taxes_id.ids)],
                    'date_status': rec.date_status,
                    'date_delivery': rec.date_delivery,
                    'color_num': rec.color_num,
                    'teeth_num_ids': [(6, 0, rec.teeth_num.ids)],
                    'discount': rec.discount,
                }
                line_values.append([0, False, values])
                mo_list_ids.append(rec.id)
            else:
                raise UserError(_('You cant create invoice because one of the already invoiced'))

        if line_values:
            invoice_obj = self.env['account.invoice']
            if not journal_id:
                raise UserError(_('Please define an accounting sales journal for this company.'))

            invoice = invoice_obj.create({
                'name': self.number,
                'origin': 'Multi manufacturing order',
                'type': 'out_invoice',
                'account_id': partner.property_account_receivable_id.id,
                'partner_id': partner.id,
                'partner_shipping_id': partner.id,
                'journal_id': journal_id,
                'payment_term_id': partner.property_payment_term_id.id or False,
                'company_id': self.env.user.company_id.id,
                'user_id': self.env.uid,
                'mo_ids': [(6, 0, mo_list_ids)],
                'invoice_line_ids': line_values,
            })
            invoice.action_invoice_open()

            for mo_rec in mo_list_ids:
                self.env['dental'].browse(mo_rec).invoice_id = invoice.id
                self.env['dental'].browse(mo_rec).state = 'invoice'


class PricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    _sql_constraints = [
        ('product_uniq', 'unique(product_tmpl_id, pricelist_id)',
         'Constraints with the same product in the same pricelist.'),
    ]

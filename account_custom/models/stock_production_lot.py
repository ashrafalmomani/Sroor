# -*- coding: utf-8 -*-

from odoo import api, models, _
from odoo.exceptions import UserError


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    _sql_constraints = [
        ('name_ref_uniq', 'Check(1=1)', 'The combination of serial number and product must be unique !'),
    ]

    @api.constrains('name', 'product_id')
    def _check_lot(self):
        for rec in self:
            lot_ids = self.env['stock.production.lot'].search([('name', '=', rec.name)])
            product = rec.product_id.id
            for lot in lot_ids:
                if product != lot.product_id.id:
                        raise UserError(_('Can not used this lot for multi product.'))

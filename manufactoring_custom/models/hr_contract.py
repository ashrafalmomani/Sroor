# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Contract(models.Model):
    _inherit = 'hr.contract'

    transportation_allowance_value = fields.Float('Transportation')
    housing_allowance_value = fields.Float('Housing')
    mobile_allowance_value = fields.Float('Mobile')
    food_allowance_value = fields.Float('Food')
    other_allowance_value = fields.Float('Other')
    total_salary = fields.Float('Total Salary', compute='_compute_total_salary')

    @api.depends('wage', 'housing_allowance_value', 'mobile_allowance_value',
                 'transportation_allowance_value', 'food_allowance_value', 'other_allowance_value')
    def _compute_total_salary(self):
        for contract in self:
            contract.total_salary = contract.wage + contract.transportation_allowance_value + \
                                    contract.housing_allowance_value + contract.food_allowance_value + \
                                    contract.mobile_allowance_value + contract.other_allowance_value

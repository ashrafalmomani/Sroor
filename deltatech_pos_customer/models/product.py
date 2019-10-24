# coding=utf-8

from odoo import models, fields, api, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    credit_journal = fields.Boolean(string="IS Credit")


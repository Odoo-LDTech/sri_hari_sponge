# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class YieldReport(models.Model):
    _name = 'yield.report'
    _description = 'Yield Report'

    manufacturing_id = fields.Many2one("mrp.production", string="Manufacturing Order No.")
    batch_id = fields.Many2one("stock.lot", string="Batch")
    input_head_on = fields.Float(string="Input")
    output_head_off = fields.Float(string="Output")
    yield_percentage = fields.Integer(string="Yield (%)")
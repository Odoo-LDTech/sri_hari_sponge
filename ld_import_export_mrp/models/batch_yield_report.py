# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class BatchYieldReport(models.Model):
	_name = 'batch.yield.report'
	_description = 'Batch Yield Report'

	batch_id = fields.Many2one("stock.lot", string="Batch")
	input_id = fields.Many2one("mrp.production", string="Input No.")
	output_id = fields.Many2one("mrp.production", string="Output No.")
	input_qty = fields.Float(string="Input Qty",compute='_compute_yield',store=True)
	output_qty = fields.Float(string="Output Qty",compute='_compute_yield',store=True)
	yield_percentage = fields.Integer(string="Yield (%)",compute='_compute_yield',store=True)
	is_approve = fields.Boolean(string="Is Approve")

	@api.depends('batch_id', 'input_id', 'output_id')
	def _compute_yield(self):
		for rec in self:
			input_qty = output_qty = yield_percentage = 0
			if rec.input_id.input_head_on:
				input_qty = rec.input_id.input_head_on
			if rec.output_id.output_head_off:
				output_qty = rec.output_id.output_head_off
			if input_qty:
				yield_percentage = (output_qty/input_qty) * 100
			rec.input_qty = input_qty
			rec.output_qty = output_qty
			rec.yield_percentage = yield_percentage

	@api.onchange('batch_id')
	def onchange_batch_id(self):
		mo_orders = self.env['mrp.production'].sudo().search([('lot_producing_id.name','=',self.batch_id.name)])
		domain = {'input_id': [('id', 'in', mo_orders.ids)],'output_id': [('id', 'in', mo_orders.ids)]}
		# domain = {'input_id': [('lot_producing_id', '=', self.batch_id.id)],'output_id': [('lot_producing_id', '=', self.batch_id.id)]}
		return {'domain': domain}

	def action_approve(self):
		self.write({
			'is_approve' : True
		})


# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class MrpProduction(models.Model):
	_inherit = 'mrp.production'

	input_head_on = fields.Float(string="Input",compute='_compute_yield',store=True)
	output_head_off = fields.Float(string="Output",compute='_compute_yield',store=True)
	yield_percentage = fields.Integer(string="Yield (%)",compute='_compute_yield',store=True)

	is_yield = fields.Boolean(string="Do you want Yield (%) ?")
	is_show_yield = fields.Boolean(string="Is Show Yield",compute='_compute_is_show_yield',store=True)
	batch_id = fields.Many2one("mrp.batch", string="Batch")

	@api.model
	def create(self, values):
		res = super(MrpProduction, self).create(values)
		check_yield = False
		if values.get('is_yield') and res.move_raw_ids:
			for move_raw in res.move_raw_ids:
				if move_raw.is_yield:
					check_yield = True
			if not check_yield:
				raise ValidationError(_("Please select a yield input line !"))
		return res

	def write(self, values):
		res = super(MrpProduction, self).write(values)
		check_yield = False
		if values.get('is_yield') and self.move_raw_ids:
			for move_raw in self.move_raw_ids:
				if move_raw.is_yield:
					check_yield = True
			if not check_yield:
				raise ValidationError(_("Please select a yield input line !"))
		return res

	# @api.depends('product_qty', 'move_raw_ids','move_raw_ids.product_uom_qty','move_byproduct_ids','move_byproduct_ids.product_uom_qty')
	@api.depends('product_qty',  'move_raw_ids', 'move_raw_ids.quantity_done','move_byproduct_ids','move_byproduct_ids.quantity_done')
	def _compute_yield(self):
		for rec in self:
			input_head_on = 0
			output_head_off = 0
			for row_line in rec.move_raw_ids:
				if row_line.is_yield:
					input_head_on = input_head_on + row_line.quantity_done
			for product_line in rec.move_byproduct_ids:
				output_head_off = output_head_off + product_line.quantity_done
			output_head_off = output_head_off + rec.product_qty
			rec.input_head_on = input_head_on
			rec.output_head_off = output_head_off
			if input_head_on:
				rec.yield_percentage = (output_head_off/input_head_on) * 100
			else:
				rec.yield_percentage = 0
			# rec.yield_percentage = 0

	@api.depends('state','is_yield')
	def _compute_is_show_yield(self):
		for rec in self:
			if rec.is_yield and rec.state == 'done':
				rec.is_show_yield = True
			else:
				rec.is_show_yield = False

	def button_mark_done(self):
		if self.move_raw_ids and not self.lot_producing_id:
			count = 1
			lot_name = None
			for move_raw in self.move_raw_ids:
				if move_raw.move_line_ids:
					for move_line in move_raw.move_line_ids:
						if move_line.lot_id and count==1:
							self.lot_producing_id = self.env['stock.lot'].create({
								'product_id': self.product_id.id,
								'company_id': self.company_id.id,
								'name': move_line.lot_id.name
							})
							lot_name = move_line.lot_id.name
							count += 1
			if lot_name and self.move_byproduct_ids:
				for move_byproduct in self.move_byproduct_ids:
					if not move_byproduct.move_line_ids:
						lot_producing_id = self.env['stock.lot'].create({
							'product_id': move_byproduct.product_id.id,
							'company_id': self.company_id.id,
							'name': lot_name
						})
						move_byproduct.move_line_ids = [(0,0,{
							'lot_id' : lot_producing_id.id,
							'qty_done' : move_byproduct.product_uom_qty,
							'product_uom_id' : move_byproduct.product_uom.id,
							'location_id' : move_byproduct.location_id.id,
							'location_dest_id' : move_byproduct.location_dest_id.id,
							'product_id' : move_byproduct.product_id.id,
						})]
		res = super(MrpProduction, self).button_mark_done()
		if self.is_yield and self.state == 'done':
			vals = {
				"manufacturing_id": self.id,
				"batch_id": self.lot_producing_id.id,
				"input_head_on": self.input_head_on,
				"output_head_off": self.output_head_off,
				"yield_percentage": self.yield_percentage,
			}
			self.env["yield.report"].sudo().create(vals)
		return res

class StockMove(models.Model):
	_inherit = 'stock.move'

	is_yield = fields.Boolean(string="Select Input for yield")
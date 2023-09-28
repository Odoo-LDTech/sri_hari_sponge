# -*- coding: utf-8 -*-
from num2words import num2words
from odoo import models, fields, api, _

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	date_ref = fields.Date('Date Reference')
	broker_id = fields.Many2one('res.partner','Broker')

class SaleOrderReport(models.AbstractModel):
    _name = 'report.sale_order_report.report_saleorder_custom'
    _description = 'Sale Order Report'

    @api.model
    def _get_report_values(self,docids,data=None):
        docs = self.env['sale.order'].browse(docids)

        def amount_num2word(amt):
            return num2words(amt).title()

        return {
            'docs': docs,
            'amount_num2word':amount_num2word,
        }
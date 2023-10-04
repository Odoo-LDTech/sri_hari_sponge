# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class MrpBatch(models.Model):
    _name = 'mrp.batch'

    name = fields.Char(string="Batch")

    @api.constrains('name')
    def _check_field_length(self):
        for record in self:
            if len(record.name) > 6:
                raise ValidationError("The Batch cannot have more than 6 characters!")

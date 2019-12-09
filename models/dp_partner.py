# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ih_res_partner(models.Model):
	_inherit = 'res.partner'
	
	revenue_shared = fields.Float(string="Rev. Shared", default=False)

# class alima_laundry(models.Model):
#     _name = 'alima_laundry.alima_laundry'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100
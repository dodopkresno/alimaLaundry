# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ih_res_partner(models.Model):
	_inherit = 'res.partner'
	
	revenue_shared = fields.Float(string="Rev. Shared", default=False)


# class ExtraWork(models.Model):
#     _name = 'wash.order.line'

#     wash_obj = fields.Many2one('washing.washing', string='Order Reference', ondelete='cascade')
#     user_id = fields.Many2one('res.users', string='Assigned Person')
#     name = fields.Char(string='Work', related='wash_obj.name', readonly=True)
#     description = fields.Text(string='Description', related='wash_obj.name', readonly=True)
#     product_id = fields.Many2one('product.product', string='Product')
#     state = fields.Selection([
#         ('draft', 'Draft'),
#         ('process', 'Process'),
#         ('done', 'Done'),
#         ('cancel', 'Cancelled'),
#     ], string='Status', readonly=True, copy=False, index=True, default='draft')
    
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
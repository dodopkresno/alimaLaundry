# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError

#inherit Sales Order
class LaundryOrder(model.Model):
    _inherit = 'sale.order'

    def estimate_end_date (self):
        return fields.date.to_string(datetime.now() + timedelta(2))

    is_laundry = fields.boolean(string='Laundry')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('open', 'Open'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')
    lo_date = fields.Date(string='Order Date', readonly=True, index=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, default=fields.Date.today) #set to required true if is laundry true
    lo_commitment_date = fields.Date('Commitment Date', states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False, readonly=True, default=estimate_end_date) #set to required true if is laundry true
    laundry_person = fields.Many2one('res.users', string='Laundry Person', index=True, track_visibility='onchange', track_sequence=2, default=lambda self: self.env.user, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    note = fields.Text(string='Remarks')

    @api.multi
    def action_confirm(self):
        super(LaundryOrder, self).action_confirm()
        if self.is_laundry:
            self.write({'state': 'open'})
            #insert into Laundry WO
            lo_wo_obj = self.env['laundry.work.order'].create({'sale_obj': self.id})
            #insert into Laundry WO Line
            for each in self:
		    #Check WO/ order Line (check git)
                if not each.order_line:
                    raise ValidationError(_('''Order haven't lines. Please create order line(s)''')) 

                #insert into Laundry WO Line
                wo_lines = []
                for obj in each.order_line:
                    qty_item = obj.product_uom_qty
                    if obj.work_type == 'wash':
                        #loop so line insert to woline based on qty
                        qty_insertw = 1
                        while qty_insertw <= qty_item:
                            lo_woline_obj = self.env['laundry.work.line'].create({'product_id': obj.product_id.id,
                                                                                'uom_id':obj.product_id.uom_id.id,
                                                                                'laundry_obj':lo_wo_obj.id})
                            wo_lines.append(lo_woline_obj.id)
                            qty_insertw += 1
                    elif obj.work_type == 'extra_work':
                        qty_inserte = 1
                        while qty_inserte <= qty_item:
                            self.env['laundry.work.line'].create({'product_id': obj.product_id.id,
                                                              'uom_id':obj.product_id.uom_id.id,
                                                              'laundry_works': True,
                                                              'laundry_obj':lo_wo_obj.id})
                            wo_lines.append(lo_woline_obj.id)
                            qty_inserte += 1
                        #lo_wo_obj.write({'outstanding_extra': obj.product_uom_qty })
                lo_wo_obj.write({'order_lines': wo_lines })
        return True
#inherit
class LaundryOrderLine(model.Models):
    _inherit = 'sale.order.line'

    work_type = fields.Many2one('work.type', string='Work Type', required=True) #menjadi filter di view

    @api.onchange('work_type')
    def _onchange_work_type(self):
        if self.order_id.is_laundry:
            if self.work_type:
                product_ids = self.env['product.product'].search([('work_type', '=', self.work_type)])
                return {
                    'domain': {
                        'product_id': [('id', 'in', product_ids)]
                    }
                }
#inherit 
class ProductProduct(models.Model):
    _inherit = 'product.product'
 
    work_type = fields.Many2one('work.type', string='Work Type')
#inherit
class IhResPartner(models.Model):
	_inherit = 'res.partner'
	
	revenue_shared = fields.Float(string="Rev. Shared", digits=(6,2))

class LaundryWorkManagement(models.Model):
    _name = 'laundry.work.order'
    _inherit = 'mail.thread'
    _description = "Laundry Work Order"
    _order = 'order_date desc, id desc'

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('laundry.work.order')
        return super(LaundryWorkManagement, self).create(vals)

    @api.multi
    def lo_execute(self):
        self.state = 'draft'
        for each in self:
            for obj in each.order_lines:
                if not obj.laundry_works:
                    if obj.assigned_person:
                        self.env['washing.washing'].create({'name': obj.product_id.name,
                                                    'product_id': obj.product_id.id,
                                                    'user_id': obj.assigned_person.id,
                                                    'description': 'Washing - ' + obj.description,
                                                    'laundry_line_obj': obj.id,
                                                    'state': 'draft',
                                                    'washing_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
                    else:
                        raise ValidationError(_('''Assigned person doesn't assigned yet. Please choose the assigned person'''))
                else:
                    if not obj.assigned_person:
                        raise ValidationError(_('''Assigned person doesn't assigned yet. Please choose the assigned person'''))
    # @api.multi
    # def return_dress(self):
    #     self.state = 'return'

    # @api.multi
    # def cancel_order(self):
    #     self.state = 'cancel'

    @api.multi
    def _work_count(self):
        wrk_ordr_ids = self.env['washing.washing'].search([('laundry_line_obj.laundry_obj.id', '=', self.id)])
        self.work_count = len(wrk_ordr_ids)

    @api.multi
    def action_view_laundry_works(self):
        work_obj = self.env['washing.washing'].search([('laundry_line_obj.laundry_obj.id', '=', self.id)])
        work_ids = []
        for each in work_obj:
            work_ids.append(each.id)
        view_id = self.env.ref('laundry_management.washing_form_view').id
        if work_ids:
            if len(work_ids) <= 1:
                value = {
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'washing.washing',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'name': _('Works'),
                    'res_id': work_ids and work_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', work_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'washing.washing',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name': _('Works'),
                    'res_id': work_ids
                }

            return value

    name = fields.Char(string='Label', copy=False)
    sale_obj = fields.Many2one('sale.order', string="Order Ref.", readonly=True)
    work_count = fields.Integer(compute='_work_count', string='# Works')
    #partner as customer
    partner_id = fields.Char(string='Customer', related = 'sale_obj.partner_id', readonly=True)
    order_date = fields.Datetime(string="Order Date", related ='sale_obj.lo_date', readonly=True)
    estimated_od_date = fields.Datetime(string="Estimated Finish", related='sale_obj.lo_commitment_date', readonly=True)
    actual_finish = fields.Datetime(string="Actual Date", default=fields.Date.today)
    order_lines = fields.One2many('laundry.work.line', 'laundry_obj', ondelete='cascade')
    remarks = fields.Text(string='Sales Remarks', related = 'sale_obj.remarks', readonly=True)
    #outstanding_extra = fields.Integer(String='Outstanding EW Item(s)')
    state = fields.Selection([
        ('draft', 'Open'),
        ('process', 'Processing'),
        ('done', 'Done'),
        ('return', 'Returned'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

class LaundryWorkLine(models.Model):
    _name = 'laundry.work.line'

    #should be have sequence or name
    name = fields.Char(string='Line Label', copy=False)
    product_id = fields.Many2one('product.product', string='Item(s)', required=True, readonly=True)
    uom_id = fields.Many2one('product.uom', 'Unit of Measure ', required=True)
    description = fields.Text(string='Description')
    parent = fields.Many2one('laundry.work.line', string = 'Main')
    child_ids = fields.One2many('laundry.work.line', 'parent', ondelete='cascade')
    laundry_works = fields.Boolean(default=False, invisible=True)
    laundry_obj = fields.Many2one('laundry.work.order', invisible=True)
    assigned_person = fields.Many2one('res.users', string='Assigned Person') 
    state = fields.Selection([
        ('draft', 'Open'),
        ('wash', 'Washing'),
        ('extra_work', 'Make Over'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, default='draft')
#in config menu    
class WorkType(models.Model):
    _name = 'work.type'

    #Wash, Extra Work

    code = fields.Char(string='Reference', required=True)
    name = fields.Char(string='Name', required=True)

    @api.constrains('code')
    def check_code(self):
		trcode = self.search([('code', '=', self.code),
							('id', 'not in', self.ids)])
		if trcode:
			raise ValidationError(_('''The code you have entered 
			already exist. Please enter different code!'''))

class Washing(models.Model):
    _name = 'washing.washing'

    @api.multi
    def start_wash(self):
        if not self.laundry_works:
            self.laundry_line_obj.state = 'wash'
            self.laundry_line_obj.laundry_obj.state = 'process'

        self.state = 'process'

    @api.multi
    def set_to_done(self):
        self.state = 'done'
        if not self.laundry_works:
            if self.laundry_line_obj.laundry_works:
                for each in self.laundry_line_obj.child_ids:
                    self.create({'name': each.name,
                        'product_id': self.laundry_line_obj.product_id.id,
                        'user_id': self.laundry_line_obj.assigned_person.id,
                        'description': 'Make Over - ' + self.laundry_line_obj.description,
                        'laundry_line_obj': self.laundry_line_obj.id,
                        'state': 'draft', #review
                        'laundry_works': True,
                        'washing_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

                self.laundry_line_obj.state = 'extra_work'
        #Check Complete All
        all_comp = True
        data = self.search([('state','in',('draft','process'))])
        if data:
            all_comp = False

        if all_comp:
            self.laundry_line_obj.laundry_obj.state = 'done'
        
    name = fields.Char(string='Work')
    laundry_works = fields.Boolean(default=False, invisible=1)
    user_id = fields.Many2one('res.users', string='Assigned Person')
    washing_date = fields.Datetime(string='Date')
    description = fields.Text(string='Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, default='draft')
    laundry_line_obj = fields.Many2one('laundry.work.line', invisible=True)
    product_line = fields.One2many('wash.order.line', 'wash_obj', string='Products', ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product')

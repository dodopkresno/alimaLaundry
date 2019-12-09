# -*- coding: utf-8 -*-
from odoo import http

# class AlimaLaundry(http.Controller):
#     @http.route('/alima_laundry/alima_laundry/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/alima_laundry/alima_laundry/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('alima_laundry.listing', {
#             'root': '/alima_laundry/alima_laundry',
#             'objects': http.request.env['alima_laundry.alima_laundry'].search([]),
#         })

#     @http.route('/alima_laundry/alima_laundry/objects/<model("alima_laundry.alima_laundry"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('alima_laundry.object', {
#             'object': obj
#         })
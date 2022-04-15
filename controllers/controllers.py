# -*- coding: utf-8 -*-
# from odoo import http


# class ImoferPlanCharge(http.Controller):
#     @http.route('/imofer_plan_charge/imofer_plan_charge', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/imofer_plan_charge/imofer_plan_charge/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('imofer_plan_charge.listing', {
#             'root': '/imofer_plan_charge/imofer_plan_charge',
#             'objects': http.request.env['imofer_plan_charge.imofer_plan_charge'].search([]),
#         })

#     @http.route('/imofer_plan_charge/imofer_plan_charge/objects/<model("imofer_plan_charge.imofer_plan_charge"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('imofer_plan_charge.object', {
#             'object': obj
#         })

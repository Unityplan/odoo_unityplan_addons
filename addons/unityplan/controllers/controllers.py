# -*- coding: utf-8 -*-
# from odoo import http


# class Unityplan(http.Controller):
#     @http.route('/unityplan/unityplan', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/unityplan/unityplan/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('unityplan.listing', {
#             'root': '/unityplan/unityplan',
#             'objects': http.request.env['unityplan.unityplan'].search([]),
#         })

#     @http.route('/unityplan/unityplan/objects/<model("unityplan.unityplan"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('unityplan.object', {
#             'object': obj
#         })

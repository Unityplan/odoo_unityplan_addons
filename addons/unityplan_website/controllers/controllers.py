# -*- coding: utf-8 -*-
#from odoo import http
#from odoo.http import request


# class Unityplan(http.Controller):
    # @http.route('/unityplan/hello', auth='public')
    # def index(self, **kw):
    #     return "Hello, world"
    #
    # @http.route('/check_website_profile_installed', type='http', auth='user', website=True)
    # def check_website_profile_installed(self, **kwargs):
    #     module = request.env['ir.module.module'].sudo().search(
    #         [('name', '=', 'website_profile'), ('state', '=', 'installed')], limit=1)
    #     if module:
    #         return "The addon 'website_profile' is installed."
    #     else:
    #         return "The addon 'website_profile' is not installed."

    # @http.route('/unityplan/unityplan/objects', auth='public')
    # def list(self, **kw):
    #     return http.request.render('unityplan.listing', {
    #         'root': '/unityplan/unityplan',
    #         'objects': http.request.env['users'].search([]),
    #     })
    #
    # @http.route('/unityplan/unityplan/objects/<model("unityplan.unityplan"):obj>', auth='public')
    # def object(self, obj, **kw):
    #     return http.request.render('unityplan.object', {
    #         'object': obj
    #     })

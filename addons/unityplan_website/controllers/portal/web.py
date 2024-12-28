from odoo import http
from odoo.addons.portal.controllers.web import Home as WebHome
from odoo.http import request
from ...tools.user_checks import has_completed_code_of_conduct, is_first_time_login, is_administrator

import logging

_logger = logging.getLogger(__name__)

class Home(WebHome):

    @http.route('/code_of_conduct', type='http', auth='user', website=True)
    def code_of_conduct(self, **kwargs):
        user = request.env.user
        return request.render('unityplan_website.code_of_conduct_page', {
            'user': user,
            'user_is_first_time_login': is_first_time_login(user.id),
        })

    def _login_redirect(self, uid, redirect=None):
        if not redirect:
            if is_administrator(uid):
                return super()._login_redirect(uid, redirect=redirect)

            if not has_completed_code_of_conduct(uid):
                redirect = '/code_of_conduct'
            else:
                redirect = '/profile/view'
        return super()._login_redirect(uid, redirect=redirect)

import werkzeug.exceptions
import werkzeug.routing
import werkzeug.urls

from odoo import models, http
from odoo.http import request
from ..tools.user_checks import (
    is_administrator,
    is_user_blocked,
    has_completed_code_of_conduct,
    is_route_allowed,
    is_route_allowed_no_login
)


class CustomIrHttp(models.AbstractModel):
    _inherit = ['ir.http']

    @classmethod
    def _match(cls, path):
        # Check if user is authenticated
        # If not authenticated
        if request.session.uid is None:
            # Check if user is allowed to access the requested page
            if not is_route_allowed_no_login(path):
                # Redirect to login page if not authenticated and not allowed to access the requested page
                werkzeug.exceptions.abort(request.redirect_query('/web/login', request.httprequest.args, code=307))

        # User is authenticated
        else:
            # Check if user is an administrator
            if is_administrator(request.session.uid):
                # Allow access to all routes for administrators
                rule, args = super()._match(path)
                return rule, args

            # Check if user is blocked
            if is_user_blocked(request.session.uid):
                # Check if user is allowed to access the requested page
                if not is_route_allowed(path):
                    # Redirect to blocked page if user is blocked and not allowed to access the requested page
                    werkzeug.exceptions.abort(request.redirect_query('/profile/blocked', request.httprequest.args, code=307))

            # Check if user has completed code of conduct
            if not has_completed_code_of_conduct(request.session.uid):
                # Check if user is allowed to access the requested page
                if not is_route_allowed(path):
                    # Redirect to code of conduct page and net allowed to access the requested page
                    werkzeug.exceptions.abort(request.redirect_query('/code_of_conduct', request.httprequest.args, code=307))

        # Allow access to the requested page, if user is authenticated and allowed to access the requested page
        rule, args = super()._match(path)
        return rule, args


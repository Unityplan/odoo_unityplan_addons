import re
from datetime import datetime
from odoo.http import request
from odoo import fields


# allowed routes for non code of conduct completed users
ALLOWED_ROUTES = [
    r'^/web/login$',
    r'^/web/reset_password$', # Allow password reset
    r'^/web/session/logout$',
    r'^/code_of_conduct$',
    r'^/profile/.*',  # Allow all sub-routes under /profile/
    r'^/my/.*',  # Allow all sub-routes under /my/
    r'^/web/image.*',  # Allow images
    r'^/web/static/.*',  # Allow static assets
    r'^/web/assets/.*',  # Allow assets
    r'^/web/bundle/.*',  # Allow bundle assets
    r'^/web/session/.*',  # Allow session routes
    r'^/web/webclient/.*',  # Allow session routes
    r'^/web/dataset/.*',  # Allow session routes
    r'^/$',  # Allow exact match for front page
    r'^/websocket$',  # Allow exact match for front page
    r'^/website/translations/.*',  # Allow translations
]

# allowed routes for blocked portal users
ALLOWED_ROUTES_NO_LOGIN = [
    r'^/web/login$',
    r'^/web/session/logout$',
    r'^/web/reset_password$', # Allow password reset
    r'^/profile/.*',  # Allow all sub-routes under /profile/
    r'^/my/.*',       # Allow all sub-routes under /my/
    r'^/web/image/.*',  # Allow images
    r'^/web/static/.*',  # Allow static assets
    r'^/web/assets/.*',  # Allow assets
    r'^/web/bundle/.*',  # Allow bundle assets
    r'^/web/session/.*',  # Allow session routes
    r'^/web/webclient/.*',  # Allow session routes
    r'^/web/dataset/.*',  # Allow session routes
    r'^/$',  # Allow exact match for front page
    r'^/websocket$',  # Allow exact match for front page
    r'^/website/translations/.*',  # Allow translations
]


def is_route_allowed(route):
    for allowed_route in ALLOWED_ROUTES:
        if re.match(allowed_route, route):
            return True
    return False


def is_route_allowed_no_login(route):
    for allowed_route in ALLOWED_ROUTES_NO_LOGIN:
        if re.match(allowed_route, route):
            return True
    return False


def is_first_time_login(uid):
    user = request.env['res.users'].sudo().browse(uid)
    if user.first_login_date:
        today = datetime.today().date()
        first_login_date = fields.Datetime.from_string(user.first_login_date).date()
        return first_login_date == today
    return False

def is_user_blocked(uid):
    user = request.env['res.users'].sudo().browse(uid)
    return not user.active


def has_completed_code_of_conduct(uid):
    user = request.env['res.users'].sudo().browse(uid)
    return user.has_group('unityplan.group_code_of_conduct_completed')


def is_administrator(uid):
    user = request.env['res.users'].sudo().browse(uid)
    return user.has_group('base.group_system')

def has_feature_preview_access(uid):
    user = request.env['res.users'].sudo().browse(uid)
    return user.has_group('unityplan.group_feature_preview')

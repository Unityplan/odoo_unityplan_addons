# -*- coding: utf-8 -*-
import json

from werkzeug import urls

from odoo import http, tools, _, SUPERUSER_ID
from odoo.http import request
from odoo.exceptions import AccessDenied, AccessError, MissingError, UserError, ValidationError

from odoo.addons.website_profile.controllers.main import WebsiteProfile
from ...tools.user_checks import has_feature_preview_access
import pytz

import logging
import re
import base64
import phonenumbers

from ...tools.languages import *

_logger = logging.getLogger(__name__)


# Extend the WebsiteProfile class to add custom methods
class ExtendedWebsiteProfile(WebsiteProfile):
    @staticmethod
    def _prepare_user_values(**kwargs):
        kwargs.pop('edit_translations', None)  # avoid nuking edit_translations
        values = {
            'uid': request.env.user.id,
            'user': request.env.user,
            'is_public_user': request.website.is_public_user(),
            'validation_email_sent': request.session.get('validation_email_sent', False),
            'validation_email_done': request.session.get('validation_email_done', False),
            'is_preview_tester': has_feature_preview_access(request.env.user.id),
            'spoken_languages_json': request.env.user.partner_id.spoken_languages_json,
            'profile_sharing_is_mobile_visible': request.env.user.partner_id.profile_sharing_is_mobile_visible,
            'profile_sharing_is_phone_visible': request.env.user.partner_id.profile_sharing_is_phone_visible,
            'profile_sharing_is_map_visible': request.env.user.partner_id.profile_sharing_is_map_visible,
            'profile_sharing_is_city_visible': request.env.user.partner_id.profile_sharing_is_city_visible,
            'profile_sharing_is_address_visible': request.env.user.partner_id.profile_sharing_is_address_visible,
            'profile_sharing_is_email_visible': request.env.user.partner_id.profile_sharing_is_email_visible,
        }
        return values

    @staticmethod
    def _prepare_user_profile_values(user, **post):
        countries = request.env['res.country'].search([])
        states = request.env['res.country.state'].search([])
        languages = request.env['res.lang'].search([]).read(['code', 'name'])
        timezones = [tz for tz in pytz.all_timezones]

        return {
            'states': states,
            'countries': countries,
            'languages': languages,
            'timezones': timezones,
            'portal_url': '/profile/view#profile',
            'uid': request.env.user.id,
            'user': user,
            'main_object': user,
            'is_profile_page': True,
            'edit_button_url_param': '',
        }

    @staticmethod
    def _prepare_view_user_profile_values(user_id, **kwargs):
        kwargs.pop('edit_translations', None)  # avoid nuking edit_translations
        # Fetch the user record
        user = request.env['res.users'].sudo().browse(user_id)
        if not user.exists():
            raise request.not_found()

        spoken_languages = json.loads(user.partner_id.spoken_languages_json or '[]')
        # Prepare values
        values = {
            'user': user,
            'spoken_languages_json': spoken_languages,
        }
        return values

    @staticmethod
    def _check_user_profile_access(user_id):
        """ Takes a user_id and returns:
            - (user record, False) when the user is granted access
            - (False, str) when the user is denied access
            Raises a Not Found Exception when the profile does not exist
        """
        # Get the user record. Use sudo() to bypass access rights
        user_sudo = request.env['res.users'].sudo().browse(user_id)
        # User can access - no matter what - users own profile
        if user_sudo.id == request.env.user.id:
            return user_sudo, False
        # Check if user have enough karma to view other users' profile
        # if request.env.user.karma < request.website.karma_profile_min:
        #     return False, _("Not have enough karma to view other users' profile.")
        # If the user is not found, raise a 404
        elif not user_sudo.exists():
            raise request.not_found()
        # If the users karma is 0 or their profile is not published, deny access
        elif not user_sudo.website_published:
            return False, _('This users profile is not published.')
        return user_sudo, False

    @http.route('/profile/view', type='http', auth="user", website=True)
    def user_profile_personal(self, **post):
        # Get the user id of the current user
        user = request.env.user
        # Check if the user is allowed to view the profile, and show the denial reason if not
        user_sudo, denial_reason = self._check_user_profile_access(user.id)
        if denial_reason:
            return request.render('website_profile.profile_access_denied', {'denial_reason': denial_reason})

        values = self._prepare_user_values(**post)
        params = self._prepare_user_profile_parameters(**post)
        values.update(self._prepare_user_profile_values(user, **params))
        values['get_error'] = get_error
        values.update({
            'portal_redirect': '/profile/view',
            'form_save_redirect': '',  # using default value for form '/profile/view#profile',
        })
        return request.render("unityplan_website.user_profile_personal_page", values)

    @http.route(['/profile/user/<int:user_id>'], type='http', auth="public", website=True)
    def view_user_profile(self, user_id, **post):
        # Check if the user is allowed to view the profile
        user_sudo, denial_reason = self._check_user_profile_access(user_id)
        if denial_reason:
            return request.render('website_profile.profile_access_denied', {'denial_reason': denial_reason})

        values = self._prepare_view_user_profile_values(user_id, **post)
        values['get_error'] = get_error
        values.update({
            'page_name': 'Member Profile: %s' % values['user'].name,
            #'portal_url': '/profile/view#profile',
            #'portal_redirect': '/profile/view',
            #'form_save_redirect': '',  # using default value for form '/profile/view#profile',
        })
        # Check if the user is the same as the current user
        # if request.env.user.id == user_id:
        #     return request.render("unityplan_website.user_profile_public_with_edit_page", values)
        # else:
        return request.render("unityplan_website.user_profile_public_page", values)

    @http.route('/profile/user/save', type='http', auth="user", methods=['POST'], website=True)
    def save_edited_profile(self, **kwargs):
        user_id = int(kwargs.get('user_id', 0))
        redirect_url = kwargs.get('form_save_redirect')
        if user_id and request.env.user.id != user_id and request.env.user._is_admin():
            user = request.env['res.users'].browse(user_id)
        else:
            user = request.env.user
        values = self._profile_edition_preprocess_values(user, **kwargs)
        values['errors'] = {'error': 'This is a test error message.'}
        values['get_error'] = get_error
        whitelisted_values = {key: values[key] for key in user.SELF_WRITEABLE_FIELDS if key in values}

        # Set map location to city if defined, else set to country
        partner = user.partner_id
        if values.get('city'):
            city = values['city']
            partner.set_location(city)
        elif values.get('country_id'):
            country = request.env['res.country'].browse(values['country_id'])
            if country.exists():
                partner.set_location(country.name)

        # Set the spoken languages
        if values.get('spoken_languages_json'):
            spoken_languages = json.loads(values['spoken_languages_json'])
            partner.spoken_languages_json = json.dumps(spoken_languages)

        # Save the new values to the user record
        user.write(whitelisted_values)
        # Redirect the user to the profile page
        if redirect_url:
            return request.redirect(redirect_url)
        elif kwargs.get('url_param'):
            return request.redirect("/profile/user/%d?%s" % (user.id, kwargs['url_param']))
        else:
            return request.redirect("/profile/user/%d" % user.id)

    @http.route('/profile/edit', type='http', auth="user", website=True)
    def view_user_profile_edition(self, **kwargs):
        user_id = int(kwargs.get('user_id', 0))
        countries = request.env['res.country'].search([])
        if user_id and request.env.user.id != user_id and request.env.user._is_admin():
            user = request.env['res.users'].browse(user_id)
            values = self._prepare_user_values(searches=kwargs, user=user, is_public_user=False)
        else:
            values = self._prepare_user_values(searches=kwargs)
        values['errors'] = {'error': 'This is a test error message.'}
        values['get_error'] = get_error
        values.update({
            'page_name': 'Edit Profile',
            'portal_url': '/profile/view#profile',
            'portal_redirect': '/profile/edit',
            'form_save_redirect': '/profile/edit',
            'email_required': kwargs.get('email_required'),
            'countries': countries,

        })
        return request.render("unityplan_website.user_profile_edit_page", values, headers={
            'X-Frame-Options': 'SAMEORIGIN',
            'Content-Security-Policy': "frame-ancestors 'self'",
        })

    @http.route(['/profile/delete_account'], type='http', auth='user', website=True, methods=['GET', 'POST'])
    def delete_account(self, validation=None, password=None, **post):
        # Get the user id of the current user
        user = request.env.user.id
        # Check if the user is allowed to view the profile, and show the denial reason if not
        user_sudo, denial_reason = self._check_user_profile_access(user.id)
        if denial_reason:
            return request.render('website_profile.profile_access_denied', {'denial_reason': denial_reason})

        values = self._prepare_user_values(**post)
        params = self._prepare_user_profile_parameters(**post)
        values.update(self._prepare_user_profile_values(user, **params))
        values['get_error'] = get_error
        values.update({
            'page_name': 'Delete Account',
        })

        values['open_deactivate_modal'] = False

        if validation != request.env.user.login:
            values['errors'] = {'deactivate': 'validation'}
        else:
            try:
                request.env['res.users']._check_credentials(password, {'interactive': True})
                request.env.user.sudo()._deactivate_portal_user(**post)
                request.session.logout()
                return request.redirect('/web/login?message=%s' % urls.url_quote(_('Account deleted!')))
            except AccessDenied:
                values['errors'] = {'deactivate': 'password'}
            except UserError as e:
                values['errors'] = {'deactivate': {'other': str(e)}}

        return request.render("unityplan_website.user_profile_delete_account_page", values, headers={
            'X-Frame-Options': 'SAMEORIGIN',
            'Content-Security-Policy': "frame-ancestors 'self'",
        })

    @http.route(['/profile/blocked'], type='http', auth='user', website=True)
    def blocked_account(self):
        # Get the user id of the current user
        user_id = request.env.user.id
        # Check if the user is allowed to view the profile, and show the denial reason if not
        user_sudo, denial_reason = self._check_user_profile_access(user_id)
        if denial_reason:
            return request.render('website_profile.profile_access_denied', {'denial_reason': denial_reason})

        values = {
            'uid': request.env.user.id,
            'user': request.env.user,
            'page_name': 'Your account is blocked',
        }
        values['get_error'] = get_error

        return request.render("unityplan_website.user_profile_blocked_account_page", values, headers={
            'X-Frame-Options': 'SAMEORIGIN',
            'Content-Security-Policy': "frame-ancestors 'self'",
        })

    @http.route(['/profile/change_password'], type='http', auth='user', website=True, methods=['GET', 'POST'])
    def change_password(self, **post):
        values = self._prepare_user_values(**post)
        values['get_error'] = get_error
        values.update({
            'page_name': 'Change Password',
        })

        if request.httprequest.method == 'POST':
            values.update(self._update_password(
                post['old'].strip(),
                post['new1'].strip(),
                post['new2'].strip()
            ))
            if 'success' in values:
                request.session.logout()
                return request.redirect('/web/login?message=%s' % urls.url_quote(
                    _('Password changed, please log in again.')))

        return request.render('unityplan_website.user_profile_change_password_page', values, headers={
            'X-Frame-Options': 'SAMEORIGIN',
            'Content-Security-Policy': "frame-ancestors 'self'"
        })

    @http.route(['/profile/revoke_sessions'], type='http', auth='user', website=True, methods=['GET', 'POST'])
    def revoke_sessions(self, **post):
        values = self._prepare_user_values(**post)
        values['get_error'] = get_error
        values.update({
            'page_name': 'Revoke Sessions',
        })

        return request.render('unityplan_website.user_profile_revoke_sessions_page', values, headers={
            'X-Frame-Options': 'SAMEORIGIN',
            'Content-Security-Policy': "frame-ancestors 'self'"
        })

    @http.route('/profile/configure_totp', type='http', auth='user', website=True)
    def show_totp_form(self, **post):
        # Get the user id of the current user
        user = request.env.user.id
        # Check if the user is allowed to view the profile, and show the denial reason if not
        user_sudo, denial_reason = self._check_user_profile_access(user.id)
        if denial_reason:
            return request.render('website_profile.profile_access_denied', {'denial_reason': denial_reason})

        values = self._prepare_user_values(**post)
        params = self._prepare_user_profile_parameters(**post)
        values.update(self._prepare_user_profile_values(user, **params))
        values['get_error'] = get_error
        values.update({
            'page_name': 'Change Multi-Factor Authentication',
        })
        values['open_deactivate_modal'] = False
        return request.render('unityplan_website.user_profile_change_totp', values, headers={
            'X-Frame-Options': 'SAMEORIGIN',
            'Content-Security-Policy': "frame-ancestors 'self'"
        })

    @http.route('/profile/rpc/get_states', type='json', auth='user')
    def rpc_get_states(self, country_id):
        states = request.env['res.country.state'].search([('country_id', '=', int(country_id))])
        return states.read(['id', 'name'])

    @http.route('/profile/rpc/get_languages_index', type='json', auth='user')
    def rpc_get_languages_index(self):
        languages = get_language_index_letter()
        return languages

    @http.route('/profile/rpc/get_languages_by_letter', type='json', auth='user')
    def rpc_get_languages_by_letter(self, letter):
        languages = get_languages_by_first_letter(letter)
        return languages

    @http.route('/profile/rpc/get_top25_languages', type='json', auth='user')
    def rpc_get_top25_languages(self):
        languages = get_top25_languages()
        return languages

    @http.route('/profile/rpc/clear_image', type='json', auth="user")
    def rpc_clear_user_image(self):
        user = request.env.user
        if not user.exists():
            return {'success': False, 'error': 'User not found'}

        # Clear the current image
        user.write({'image_1920': False})

        # Generate the default image URL
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        default_image_url = base_url + '/web/image?' + 'model=res.users&id=' + str(user.id) + '&field=avatar_128'
        return {'success': True, 'new_image_url': default_image_url}

    @staticmethod
    def _validate_new_password(self, password):
        if len(password) < 10:
            return _("The new password must be at least 10 characters long.")
        if not re.search(r'[A-Z]', password):
            return _("The new password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            return _("The new password must contain at least one lowercase letter.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return _("The new password must contain at least one special character.")
        return None

    def _update_password(self, old, new1, new2):
        for k, v in [('old', old), ('new1', new1), ('new2', new2)]:
            if not v:
                return {'errors': {'password': {k: _("You cannot leave any password empty.")}}}

        if new1 != new2:
            return {'errors': {'password': {'new2': _("The new password and its confirmation must be identical.")}}}

        if new1 == old:
            return {'errors': {'password': {'new1': _("The new password must be different from the old password.")}}}

        validation_error = self._validate_new_password(self, new1)
        if validation_error:
            return {'errors': {'password': {'new1': validation_error}}}

        try:
            request.env['res.users'].change_password(old, new1)
        except AccessDenied as e:
            msg = e.args[0]
            if msg == AccessDenied().args[0]:
                msg = _('The old password you provided is incorrect, your password was not changed.')
            return {'errors': {'password': {'old': msg}}}
        except UserError as e:
            return {'errors': {'password': e.name}}

        # update session token so the user does not get logged out (cache cleared by passwd change)
        #new_token = request.env.user._compute_session_token(request.session.sid)
        #request.session.session_token = new_token

        return {'success': {'password': True}}

    def _profile_edition_preprocess_values(self, user, **kwargs):
        values = {
            'name': kwargs.get('name'),
            'website': kwargs.get('website'),
            'email': kwargs.get('email'),
            'city': kwargs.get('city'),
            'zip': kwargs.get('zip'),
            'street': kwargs.get('street'),
            'street2': kwargs.get('street2'),
            'lang': kwargs.get('lang'),
            'tz': kwargs.get('tz') if kwargs.get('tz') else False,
            'state_id': int(kwargs.get('state')) if kwargs.get('state') else False,
            'country_id': int(kwargs.get('country')) if kwargs.get('country') else False,
            'website_description': kwargs.get('description'),
            'spoken_languages_json': kwargs.get('spoken_languages_json') if kwargs.get('spoken_languages_json') else [],
            'profile_sharing_is_email_visible': kwargs.get('profile_sharing_is_email_visible') == 'on',
            'profile_sharing_is_address_visible': kwargs.get('profile_sharing_is_address_visible') == 'on',
            'profile_sharing_is_city_visible': kwargs.get('profile_sharing_is_city_visible') == 'on',
            'profile_sharing_is_map_visible': kwargs.get('profile_sharing_is_map_visible') == 'on',
            'profile_sharing_is_phone_visible': kwargs.get('profile_sharing_is_phone_visible') == 'on',
            'profile_sharing_is_mobile_visible': kwargs.get('profile_sharing_is_mobile_visible') == 'on',
        }

        phone = kwargs.get('phone')
        mobile = kwargs.get('mobile')
        country_code = None

        # Get the country code
        if kwargs.get('country'):
            country = request.env['res.country'].browse(int(kwargs.get('country')))
            if country.exists():
                country_code = country.code

        # Format the phone number
        if phone and country_code:
            try:
                phone_number = phonenumbers.parse(phone, country_code)
                values['phone'] = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            except phonenumbers.phonenumberutil.NumberParseException:
                values['phone'] = phone
        else:
            values['phone'] = phone

        # Format the mobile number
        if mobile and country_code:
            try:
                mobile_number = phonenumbers.parse(mobile, country_code)
                values['mobile'] = phonenumbers.format_number(mobile_number,
                                                              phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            except phonenumbers.phonenumberutil.NumberParseException:
                values['mobile'] = mobile
        else:
            values['mobile'] = mobile

        # Format the url to include the http:// or https:// prefix
        personal_website = kwargs.get('personal_website')
        if personal_website and not re.match(r'^(http://|https://)', personal_website):
            personal_website = 'http://' + personal_website
        values['personal_website'] = personal_website

        # Format the avatar image
        if 'clear_image' in kwargs:
            values['image_1920'] = False
        elif kwargs.get('ufile'):
            image = kwargs.get('ufile').read()
            values['image_1920'] = base64.b64encode(image)

        if request.uid == user.id:  # the controller allows to edit only its own privacy settings; use partner management for other cases
            # values['website_published'] = kwargs.get('website_published') == 'True'
            # Always set the website_published to True when saved from the profile page
            values['website_published'] = 'True'
        return values


def get_error(e, path=''):
    """ Recursively dereferences `path` (a period-separated sequence of dict
    keys) in `e` (an error dict or value), returns the final resolution IIF it's
    a str, otherwise returns None
    """
    for k in (path.split('.') if path else []):
        if not isinstance(e, dict):
            return None
        e = e.get(k)

    return e if isinstance(e, str) else None



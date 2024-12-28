# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
from odoo import fields, models, api
from odoo.http import request

import pytz
from datetime import datetime


class ResUsers(models.Model):
    """ Inherit the res.users model """
    _inherit = 'res.users'

    first_login_date = fields.Datetime(string='First Login Date', readonly=True)

    @property
    def SELF_WRITEABLE_FIELDS(self):
        """ The list of fields a user can write on their own user record.
        In order to add fields, please override this property on model extensions.
        """
        return ['signature', 'action_id', 'company_id', 'email', 'name', 'image_1920', 'lang', 'tz', 'phone', 'mobile',
                'street', 'street2', 'zip', 'city', 'state_id', 'country_id', 'website', 'personal_website',
                'website_description', 'profile_sharing_is_email_visible', 'profile_sharing_is_address_visible',
                'profile_sharing_is_city_visible', 'profile_sharing_is_map_visible',
                'profile_sharing_is_phone_visible', 'profile_sharing_is_mobile_visible',]

    @api.model
    def _session_gc(self):
        """ Set the session timeout to 1 hour """
        # Set session timeout to 1 hour (3600 seconds)
        request.session.timeout = 3600
        return super(ResUsers, self)._session_gc()

    @api.model
    def _update_first_login_date(self, uid):
        user = self.browse(uid)
        if not user.first_login_date:
            user.sudo().write({'first_login_date': fields.Datetime.now()})

    @api.model
    def _check_credentials(self, password, user_agent_env=None):
        res = super(ResUsers, self)._check_credentials(password, user_agent_env)
        self._update_first_login_date(self.env.uid)
        return res

    def _get_gmt_offset(self):
        for user in self:
            if user.tz:
                user_tz = pytz.timezone(user.tz)
                offset = user_tz.utcoffset(datetime.now()).total_seconds() / 3600
                user.gmt_offset = f"GMT{'+' if offset >= 0 else ''}{int(offset)}"
            else:
                user.gmt_offset = "GMT"

    gmt_offset = fields.Char(compute='_get_gmt_offset', string='GMT Offset')

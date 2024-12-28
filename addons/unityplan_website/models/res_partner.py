# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
from odoo import fields, models, api
from geopy.geocoders import Nominatim


class ResPartner(models.Model):
    """ Inherit the res.partner model """
    _inherit = 'res.partner'

    partner_latitude = fields.Float(string="Latitude", digits=(16, 5))
    partner_longitude = fields.Float(string="Longitude", digits=(16, 5))

    personal_website = fields.Char(
        string="Personal Website",
        help="If you have a personal website, enter it here."
    )
    website = fields.Char(
        string="Company Website",
        help="If you have a company website, enter it here."
    )

    profile_sharing_is_email_visible = fields.Boolean(
        string="Show e-mail address to members",
        default=False,
        help="Show your e-mail address to other members, on your profile page?"
    )

    profile_sharing_is_address_visible = fields.Boolean(
        string="Show address to members",
        default=False,
        help="Show your address to other members, on your profile page?"
    )
    profile_sharing_is_city_visible = fields.Boolean(
        string="Show city to members",
        default=True,
        help="Show the city, but not the entire address to other members, on your profile page? This way other people can get an idea of where you are located, without knowing your exact address."
    )
    profile_sharing_is_map_visible = fields.Boolean(
        string="Show location (city) on map, to members",
        default=True,
        help="Show your location (city) on a map, to other members, on your profile page?"
    )

    profile_sharing_is_phone_visible = fields.Boolean(
        string="Show phone to members",
        default=False,
        help="Show your phone number to other members, on your profile page?"
    )
    profile_sharing_is_mobile_visible = fields.Boolean(
        string="Show mobile to members",
        default=False,
        help="Show your mobile phone number to other members, on your profile page?"
    )

    spoken_languages_json = fields.Json(
        string="Spoken Languages",
        help="JSON list of spoken languages with priority and language code."
    )

    def set_location(self, location):
        geolocator = Nominatim(user_agent="unityplan_website")
        got_location = geolocator.geocode(location)
        if got_location:
            self.partner_latitude = got_location.latitude
            self.partner_longitude = got_location.longitude










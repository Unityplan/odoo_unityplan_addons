# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
from odoo import fields, models, api
import pytz
import logging
_logger = logging.getLogger(__name__)


class ResCountry(models.Model):
    _inherit = 'res.country'

    # Add a new field territory_type to the res.country model
    territory_type = fields.Selection([('country', 'Country'), ('first_nation', 'First Nation')],
                                      string='Territory type',
                                      help='Select if the territory type is First Nation or Country',
                                      copy=True, required=True, default='country'
                                      )

    def get_timezones_by_country(self):
        country_timezones = []
        country_code = self.code
        for country, timezones in pytz.country_timezones.items():
            if country.lower() == country_code.lower() or pytz.country_names[country].lower() == self.name.lower():
                country_timezones.extend(timezones)

        if not country_timezones:
            return pytz.all_timezones

        return country_timezones


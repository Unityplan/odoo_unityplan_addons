# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
from odoo import models, fields, api


class CountryManager(models.Model):
    _name = "res.country_manager"
    _description = 'Country Manager'
    _inherits = {'res.users': 'related_user_id'}

    is_country_manager = fields.Boolean(string='Is Country Manager', readonly=True, default=False)
    is_community_manager = fields.Boolean(string='Is Community Manager', readonly=True, default=False)
    related_user_id = fields.Many2one('res.users', required=True, ondelete='cascade', auto_join=True, index=True,
                                      string='Related user', help='User-related data of the country manager')
    # country_name = fields.Char(string='Country', compute='_compute_display_value', store=False)
    country_ids = fields.Many2many(
        'res.country',
        string='Countries',
    )



    # def _compute_display_value(self):
    #     self.country_name = self.related_user_id.partner_id.country_id.name

    # @api.model
    # def create(self, user_vals):
    #     # Fetch all portal users.
    #     # portal_users = self.env['res.country_manager'].search([
    #     #     ('share', '=', True)
    #     # ])
    #     record = super(CountryManager, self).create(user_vals)
    #     # Custom logic after creating the record
    #     return record
    #
    # def write(self, user_vals):
    #     # Define default values for new user creation
    #     # default_user_vals = {
    #     #     'share': True,  # Set user as a portal user
    #     #     'is_country_manager': True  # Set user as a country manager
    #     #     #'country_id': country_id,  # Assign user's country
    #     #     # Add other default values as needed
    #     # }
    #     # # Ensure name and email from user_vals are preserved and update with default values
    #     # user_vals = {**default_user_vals, **user_vals}
    #     result = super(CountryManager, self).write(user_vals)
    #     # Custom logic after writing to the record
    #     return result

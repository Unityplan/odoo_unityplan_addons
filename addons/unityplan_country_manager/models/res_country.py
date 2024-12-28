# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
from odoo import fields, models, api
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
    # Add a new field manager_ids to the res.country model
    manager_ids = fields.Many2many(
        'res.country_manager',
        string='Country Manager',
        ondelete='cascade',
        domain=[('related_user_id.share', '=', True)]
    )
    # Add a new field temp_user_ids_on_read to the res.country model, this will be used to store
    # the temporary user ids, but not store the data in the database
    temp_user_ids = fields.Many2many(
        'res.users',
        string='Country Managers',
        store=False,
        domain=[('share', '=', True)],
        search='_search_temp_user_ids'
    )

    @api.model
    def read(self, fields=None, load='_classic_read'):
        # Call the super method to read the fields
        result = super(ResCountry, self).read(fields, load)

        # Check if it's a form view that's being loaded
        #if self.env.context.get('view_type') == 'form' or self.env.context.get('params', {}).get('view_type') == 'form':
        if len(self.ids) == 1:
            # Loop through the result
            for record in result:
                # Get all the country managers id from the database record
                manager_ids = record.get('manager_ids', [])
                # Get a list of the user_ids from the manager_ids
                user_ids = (self.env['res.country_manager'].browse(manager_ids).mapped('related_user_id'))
                # Update temp_user_ids with the user_ids
                if user_ids:
                    record.update({'temp_user_ids': user_ids.ids})

        return result

    def create(self, vals):
        record = super(ResCountry, self).create(vals)
        # Custom logic after creating the record
        return record

    def write(self, vals):
        # Call the super method to write the vals
        result = super(ResCountry, self).write(vals)

        # Initialize the latest_added_temp_user_ids and latest_removed_temp_user_ids
        latest_added_temp_user_ids = set()
        latest_removed_temp_user_ids = set()

        # Check if the temp_user_ids field is in the vals
        if 'temp_user_ids' in vals:
            # Loop through the temp_user_ids
            for user_ids in vals['temp_user_ids']:
                # Check is user_ids was added (4) or removed (3)
                if user_ids[0] == 4:
                    # Add the user_id to the latest_added_temp_user_ids
                    latest_added_temp_user_ids.add(user_ids[1])
                elif user_ids[0] == 3:
                    # Add the user_id to the latest_removed_temp_user_ids
                    latest_removed_temp_user_ids.add(user_ids[1])

            # For each added user
            for user_id in latest_added_temp_user_ids:
                # Get the user with the user_id
                user = self.env['res.users'].browse(user_id)
                # Get the country manager object with the user_id if one exists
                manager = self.env['res.country_manager'].search([('related_user_id', '=', user.id)], limit=1)
                # If no manager exists
                if not manager:
                    # Create a new country manager with the user_id
                    manager = self.env['res.country_manager'].create({'related_user_id': user.id})

                # Set the manager as a country manager
                manager.is_country_manager = True
                # Update the manager with the country manager object
                self.manager_ids = [(4, manager.id)]

                # Check if the user's partner does not have a country set
                if not user.partner_id.country_id:
                    # Set the partner's country to the current country
                    user.partner_id.country_id = self.id

                # Check if the user's partner does not have an email set
                if not user.partner_id.email:
                    # Set the user's partner's email equal to the user's login
                    user.partner_id.email = user.login

                # Add the user to the group with the name group_unityplan_country_managers
                group = self.env.ref('unityplan_country_manager.group_unityplan_country_managers')
                if group:
                    group.users = [(4, user.id)]


            # For each removed user
            for user_id in latest_removed_temp_user_ids:
                # Get the user with the user_id
                user = self.env['res.users'].browse(user_id)
                # Get the country manager object with the user_id if one exists
                manager = self.env['res.country_manager'].search([('related_user_id', '=', user.id)], limit=1)
                # If a manager exists
                if manager:
                    # Unlink the manager
                    self.manager_ids = [(3, manager.id)]
                    # Check if the manager has no more relations
                    if not self.env['res.country'].search_count([('manager_ids', 'in', manager.id)]):
                        # Delete the manager record from the res.country_manager table
                        manager.unlink()
                        
                    # Remove the user from the group with the name group_unityplan_country_managers
                    group = self.env.ref('unityplan_country_manager.group_unityplan_country_managers')
                    if group:
                        group.users = [(3, user.id)]

        return result


    #


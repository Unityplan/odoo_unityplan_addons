# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
from odoo import fields, models, api
from odoo.http import request


class ResUsers(models.Model):
    """ Inherit the res.users model """
    _inherit = 'res.users'

    country_manager_country_ids = fields.Many2many(
        'res.country',
        compute='_compute_country_manager_country_ids',
        string='Country Manager Country IDs', store=False
    )

    is_country_manager = fields.Boolean(compute='_compute_is_country_manager')

    @api.model
    def _session_gc(self):
        """ Set the session timeout to 1 hour """
        # Set session timeout to 1 hour (3600 seconds)
        request.session.timeout = 3600
        return super(ResUsers, self)._session_gc()

    @api.depends('groups_id')
    def _compute_country_manager_country_ids(self):
        for user in self:
            if user.has_group('unityplan_country_manager.group_unityplan_country_managers'):
                country_manager = self.env['res.country_manager'].search([('related_user_id', '=', user.id)], limit=1)
                user.country_manager_country_ids = country_manager.country_ids if country_manager else False
            else:
                user.country_manager_country_ids = False

    @api.depends_context('uid')
    def _compute_is_country_manager(self):
        for user in self:
            user.is_country_manager = bool(
                self.env['res.country_manager'].search([('related_user_id', '=', user.id)], limit=1))

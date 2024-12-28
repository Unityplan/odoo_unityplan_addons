# -*- coding: utf-8 -*-
# noinspection PyUnresolvedReferences
from odoo import models, fields, api


class UnityplanDashboard(models.Model):
    """ The dashboard model """
    _name = "unityplan.dashboard"
    _description = 'Unityplan Dashboard'

    name = fields.Char(string='Dashboard', help='Dashboard', readonly=True)
    message = fields.Text(string='Coming soon...!')

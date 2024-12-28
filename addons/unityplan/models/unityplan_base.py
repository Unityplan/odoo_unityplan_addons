# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
from odoo import models, fields, api
from odoo.http import request


class UnityplanBaseModel(models.Model):
    """ The base model of the Unity Plan module for generic features """
    _name = "unityplan.base"
    _description = 'Unityplan Base Model'

    # ------------------------------------------------------------
    # UNITYPLAN SETTINGS
    # ------------------------------------------------------------
    name = fields.Char(string="Unityplan Settings")
    description = fields.Text() # Description of the Unityplan settings
    unityplan_settings = fields.Boolean(string="Unityplan Settings", default=True)


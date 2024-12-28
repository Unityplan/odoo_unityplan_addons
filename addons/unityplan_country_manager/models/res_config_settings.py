# File: dev-addons/unityplan_country_manager/models/res_config_settings.py

from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    demo_data_loaded = fields.Boolean(string="Demo Data Loaded", default=False)

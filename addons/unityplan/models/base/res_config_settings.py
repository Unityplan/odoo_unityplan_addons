# -*- coding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    """ Inherit the base settings to add a counter of failed email + configure
    the alias domain. """
    _inherit = 'res.config.settings'

    use_test_data = fields.Boolean(
        'Use test data',
        help="This is just a test of a help text",
        config_parameter='unityplan.use_test_data',
    )
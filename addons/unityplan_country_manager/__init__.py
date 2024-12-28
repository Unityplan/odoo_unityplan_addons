# -*- coding: utf-8 -*-

from . import controllers
from . import models
from odoo import api, SUPERUSER_ID

from .demo.demo_data_loader import load_demo_data

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    load_demo_data(env, registry)
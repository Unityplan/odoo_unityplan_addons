
# noinspection PyUnresolvedReferences
from odoo import models, fields, api


class Community(models.Model):
    _name = 'portal.community'
    _description = 'Community'

    name = fields.Char(required=True)
    country_id = fields.Many2one('res.country', string='Country', required=True)
    manager_ids = fields.Many2many('res.country_manager', string='Managers', domain=[('is_community_manager', '=', True)])
    #forum_post_ids = fields.One2many('portal.forum.post', 'community_id', string='Forum Posts')
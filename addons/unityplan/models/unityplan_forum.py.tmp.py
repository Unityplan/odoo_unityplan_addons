from odoo import models, fields, api


class ForumPost(models.Model):
    _name = 'portal.forum.post'
    _description = 'Forum Post'

    content = fields.Text(required=True)
    community_id = fields.Many2one('portal.community', string='Community', required=True)
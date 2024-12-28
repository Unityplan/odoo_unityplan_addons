from odoo import api, fields, models, _
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.exceptions import AccessError

class Tags(models.Model):
    _inherit = 'forum.tag'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            forum = self.env['forum.forum'].browse(vals.get('forum_id'))
            if self.env.user.karma < forum.karma_tag_create:
                raise AccessError(_('%d karma required to create a new Tag.', forum.karma_tag_create))
        return super(Tags, self.with_context(mail_create_nolog=True, mail_create_nosubscribe=True)).create(vals_list)
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

class Vote(models.Model):
    _inherit = 'forum.post.vote'

    def _check_karma_rights(self, upvote=None):
        # karma check
        if upvote and not self.post_id.can_upvote:
            raise AccessError(_('%d karma required to upvote.', self.post_id.forum_id.karma_upvote))
        elif not upvote and not self.post_id.can_downvote:
            raise AccessError(_('%d karma required to downvote.', self.post_id.forum_id.karma_downvote))
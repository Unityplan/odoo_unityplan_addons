# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, AccessError
from odoo.addons.http_routing.models.ir_http import unslug

_logger = logging.getLogger(__name__)


class UnityplanCategoryTags(models.Model):
    _inherit = 'unityplan.category.tag'

    forum_ids = fields.One2many(
        'forum.forum',
        'category',
        string='Forums',
        index=True,
        required=True,
        ondelete="cascade"
    )


class Forum(models.Model):
    _inherit = 'forum.forum'

    privacy = fields.Selection([
        ('public', 'Public'),
        ('connected', 'Signed In'),
        ('private', 'Some users')],
        help="Public: Forum is public\n"
             "Signed In: Forum is visible for signed in users\n"
             "Some users: Forum and their content are hidden for non members of selected group",
        default='connected'
    )
    category = fields.Many2one('unityplan.category.tag', 'Unity Plan Category')
    mode = fields.Selection([
        ('unityplan_questions', 'Questions (1 answer) [Unity Plan Version]'),
        ('unityplan_discussions', 'Discussions (multiple answers) [Unity Plan Version]'),
        ('questions', 'Questions (1 answer)'),
        ('discussions', 'Discussions (multiple answers)')],
        string='Mode', required=True, default='unityplan_discussions',
        help='Questions mode: only one answer allowed\n '
             'Discussions mode: multiple answers allowed\n '
             'Unity Plan Versions have special permissions'
    )
    # karma-based action permissions
    authorized_group_ask = fields.Many2one('res.groups', 'Ask questions')
    authorized_group_answer = fields.Many2one('res.groups', 'Answer questions')
    authorized_group_edit_own = fields.Many2one('res.groups', 'Edit own posts')
    authorized_group_edit_all = fields.Many2one('res.groups', 'Edit all posts')
    authorized_group_edit_retag = fields.Many2one('res.groups', 'Ehange question tags')
    authorized_group_close_own = fields.Many2one('res.groups', 'Close own posts')
    authorized_group_close_all = fields.Many2one('res.groups', 'Close all posts')
    authorized_group_unlink_own = fields.Many2one('res.groups', 'Delete own posts')
    authorized_group_unlink_all = fields.Many2one('res.groups', 'Delete all posts')
    authorized_group_tag_create = fields.Many2one('res.groups', 'Create new tags')
    authorized_group_upvote = fields.Many2one('res.groups', 'Upvote')
    authorized_group_downvote = fields.Many2one('res.groups', 'Downvote')
    authorized_group_answer_accept_own = fields.Many2one('res.groups', 'Accept an answer on own questions')
    authorized_group_answer_accept_all = fields.Many2one('res.groups', 'Accept an answer to all questions')
    authorized_group_comment_own = fields.Many2one('res.groups', 'Comment own posts')
    authorized_group_comment_all = fields.Many2one('res.groups', 'Comment all posts')
    authorized_group_comment_convert_own = fields.Many2one('res.groups', 'Convert own answers to comments and vice versa')
    authorized_group_comment_convert_all = fields.Many2one('res.groups', 'Convert all answers to comments and vice versa')
    authorized_group_comment_unlink_own = fields.Many2one('res.groups', 'Unlink own comments')
    authorized_group_comment_unlink_all = fields.Many2one('res.groups', 'Unlink all comments')
    authorized_group_flag = fields.Many2one('res.groups', 'Flag a post as offensive')
    authorized_group_dofollow = fields.Many2one('res.groups', 'Nofollow links')
    authorized_group_editor = fields.Many2one('res.groups', 'Editor Features: image and links')
    authorized_group_user_bio = fields.Many2one('res.groups', 'Display detailed user biography')
    authorized_group_post = fields.Many2one('res.groups', 'Ask questions without validation')
    authorized_group_moderate = fields.Many2one('res.groups', 'Moderate posts')

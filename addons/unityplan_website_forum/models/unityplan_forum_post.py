import logging
import math
import re
from datetime import datetime

from odoo import api, fields, models, tools, _
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.osv import expression
from odoo.tools import sql

_logger = logging.getLogger(__name__)


class Post(models.Model):
    _inherit = 'forum.post'

    @api.depends_context('uid')
    def _compute_post_karma_rights(self):
        user = self.env.user
        is_admin = self.env.is_admin()
        # sudoed recordset instead of individual posts so values can be
        # prefetched in bulk
        for post, post_sudo in zip(self, self.sudo()):
            forum = post.forum_id
            mode = forum.mode
            is_creator = post.create_uid == user

            post.karma_accept = post.forum_id.karma_answer_accept_own if post.parent_id.create_uid == user else post.forum_id.karma_answer_accept_all
            post.karma_edit = post.forum_id.karma_edit_own if is_creator else post.forum_id.karma_edit_all
            post.karma_close = post.forum_id.karma_close_own if is_creator else post.forum_id.karma_close_all
            post.karma_unlink = post.forum_id.karma_unlink_own if is_creator else post.forum_id.karma_unlink_all
            post.karma_comment = post.forum_id.karma_comment_own if is_creator else post.forum_id.karma_comment_all
            post.karma_comment_convert = post.forum_id.karma_comment_convert_own if is_creator else post.forum_id.karma_comment_convert_all
            post.karma_flag = post.forum_id.karma_flag

            # Normal Odoo forum mode without role permissions but where karma = 0 will decline permission
            if mode != "unityplan_questions" and mode != "unityplan_discussions":

                # Can ask question (create question post)
                if forum.karma_ask == 0:
                    post.can_ask = False
                else:
                    post.can_ask = is_admin or user.karma >= forum.karma_ask

                # Can answer a question
                if forum.karma_answer == 0:
                    post.can_answer = False
                else:
                    post.can_answer = is_admin or user.karma >= forum.karma_answer

                #Can accept answer on all posts
                if post.parent_id.create_uid == user:
                    if forum.karma_answer_accept_own == 0:
                        post.can_accept = False
                    else:
                        post.can_accept = is_admin or user.karma >= forum.karma_answer_accept_own
                else:
                    if forum.karma_answer_accept_all == 0:
                        post.can_accept = False
                    else:
                        post.can_accept = is_admin or user.karma >= forum.karma_answer_accept_all

                # Can upvote
                if forum.karma_upvote == 0:
                    post.can_upvote = False
                else:
                    post.can_upvote = is_admin or user.karma >= post.forum_id.karma_upvote or post.user_vote == -1

                # Can downvote
                if forum.karma_downvote == 0:
                    post.can_downvote = False
                else:
                    post.can_downvote = is_admin or user.karma >= post.forum_id.karma_downvote or post.user_vote == 1

                # TODO: Check this one
                # Can view a post
                post.can_view = post.can_close or post_sudo.active and (
                        post_sudo.create_uid.karma > 0 or post_sudo.create_uid == user)

                # Can view user bio on post
                if forum.karma_user_bio == 0:
                    post.can_display_biography = False
                else:
                    post.can_display_biography = is_admin or post_sudo.create_uid.karma >= forum.karma_user_bio

                # Can create a discussion post
                if forum.karma_post == 0:
                    post.can_post = False
                else:
                    post.can_post = is_admin or user.karma >= forum.karma_post

                # Can flag a post
                if forum.karma_flag == 0:
                    post.can_flag = False
                else:
                    post.can_flag = is_admin or user.karma >= forum.karma_flag

                # Can moderate a post
                if forum.karma_moderate == 0:
                    post.can_moderate = False
                else:
                    post.can_moderate = is_admin or user.karma >= forum.karma_moderate

                # Can use the full editor on post description
                if forum.karma_editor == 0:
                    post.can_use_full_editor = False
                else:
                    post.can_use_full_editor = is_admin or user.karma >= forum.karma_editor

                if is_creator:
                    # Can edit own post________________________________________________
                    if forum.karma_edit_own == 0:
                        post.can_edit = False
                    else:
                        post.can_edit = is_admin or user.karma >= forum.karma_edit_own
                    # Can close own post________________________________________________
                    if forum.karma_close_own == 0:
                        post.can_close = False
                    else:
                        post.can_close = is_admin or user.karma >= forum.karma_close_own
                    # Can unlink own post________________________________________________
                    if forum.karma_unlink_own == 0:
                        post.can_unlink = False
                    else:
                        post.can_unlink = is_admin or user.karma >= forum.karma_unlink_own
                    # Can comment own post________________________________________________
                    if forum.karma_comment_own == 0:
                        post.can_comment = False
                    else:
                        post.can_comment = is_admin or user.karma >= forum.karma_comment_own
                    # Can convert own comments______________________________________________
                    if forum.karma_unlink_own == 0:
                        post.can_comment_convert = False
                    else:
                        post.can_comment_convert = is_admin or user.karma >= forum.karma_comment_convert_own
                else:
                    # Can edit all posts________________________________________________
                    if forum.karma_edit_all == 0:
                        post.can_edit = False
                    else:
                        post.can_edit = is_admin or user.karma >= forum.karma_edit_all
                    # Can close all posts________________________________________________
                    if forum.karma_close_all == 0:
                        post.can_close = False
                    else:
                        post.can_close = is_admin or user.karma >= forum.karma_close_all
                    # Can unlink all posts________________________________________________
                    if forum.karma_unlink_all == 0:
                        post.can_unlink = False
                    else:
                        post.can_unlink = is_admin or user.karma >= forum.karma_unlink_all
                    # Can comment all posts________________________________________________
                    if forum.karma_comment_all == 0:
                        post.can_comment = False
                    else:
                        post.can_comment = is_admin or user.karma >= forum.karma_comment_all
                    # Can convert all comments______________________________________________
                    if forum.karma_unlink_all == 0:
                        post.can_comment_convert = False
                    else:
                        post.can_comment_convert = is_admin or user.karma >= forum.karma_comment_convert_all

            # Extended forum mode with role permissions and where karma = 0 will decline permission
            else:

                # Can ask question (create question post)
                if user in forum.authorized_group_ask.sudo().users:
                    post.can_ask = True
                elif forum.karma_ask == 0:
                    post.can_ask = False
                else:
                    post.can_ask = is_admin or user.karma >= forum.karma_ask

                # Can answer a question
                if user in forum.authorized_group_answer.sudo().users:
                    post.can_answer = True
                elif forum.karma_answer == 0:
                    post.can_answer = False
                else:
                    post.can_answer = is_admin or user.karma >= forum.karma_answer

                # Can accept answer on all posts
                if post.parent_id.create_uid == user:
                    if user in forum.authorized_group_answer_accept_own.sudo().users:
                        post.can_accept = True
                    elif forum.karma_answer_accept_own == 0:
                        post.can_accept = False
                    else:
                        post.can_accept = is_admin or user.karma >= forum.karma_answer_accept_own
                else:
                    if user in forum.authorized_group_answer_accept_all.sudo().users:
                        post.can_accept = True
                    elif forum.karma_answer_accept_all == 0:
                        post.can_accept = False
                    else:
                        post.can_accept = is_admin or user.karma >= forum.karma_answer_accept_all

                # Can upvote
                if user in forum.authorized_group_upvote.sudo().users:
                    post.can_upvote = True
                elif forum.karma_upvote == 0:
                    post.can_upvote = False
                else:
                    post.can_upvote = is_admin or user.karma >= post.forum_id.karma_upvote or post.user_vote == -1

                # Can downvote
                if user in forum.authorized_group_downvote.sudo().users:
                    post.can_downvote = True
                elif forum.karma_downvote == 0:
                    post.can_downvote = False
                else:
                    post.can_downvote = is_admin or user.karma >= post.forum_id.karma_downvote or post.user_vote == 1

                # TODO: Check this one
                # Can view a post
                post.can_view = post.can_close or post_sudo.active and (
                        post_sudo.create_uid.karma > 0 or post_sudo.create_uid == user)

                # Can view user bio on post
                if user in forum.authorized_group_user_bio.sudo().users:
                    post.can_display_biography = True
                elif forum.karma_user_bio == 0:
                    post.can_display_biography = False
                else:
                    post.can_display_biography = is_admin or post_sudo.create_uid.karma >= forum.karma_user_bio

                # Can create a discussion post
                if user in forum.authorized_group_post.sudo().users:
                    post.can_post = True
                elif forum.karma_post == 0:
                    post.can_post = False
                else:
                    post.can_post = is_admin or user.karma >= forum.karma_post

                # Can flag a post
                if user in forum.authorized_group_flag.sudo().users:
                    post.can_flag = True
                elif forum.karma_flag == 0:
                    post.can_flag = False
                else:
                    post.can_flag = is_admin or user.karma >= forum.karma_flag

                # Can moderate a post
                if user in forum.authorized_group_moderate.sudo().users:
                    post.can_moderate = True
                elif forum.karma_moderate == 0:
                    post.can_moderate = False
                else:
                    post.can_moderate = is_admin or user.karma >= forum.karma_moderate

                # Can use the full editor on post description
                if user in forum.authorized_group_editor.sudo().users:
                    post.can_use_full_editor = True
                elif forum.karma_editor == 0:
                    post.can_use_full_editor = False
                else:
                    post.can_use_full_editor = is_admin or user.karma >= forum.karma_editor

                if is_creator:
                    # Can edit own post________________________________________________
                    if user in forum.authorized_group_edit_own.sudo().users:
                        post.can_edit = True
                    elif forum.karma_edit_own == 0:
                        post.can_edit = False
                    else:
                        post.can_edit = is_admin or user.karma >= forum.karma_edit_own
                    # Can close own post________________________________________________
                    if user in forum.authorized_group_close_own.sudo().users:
                        post.can_close = True
                    elif forum.karma_close_own == 0:
                        post.can_close = False
                    else:
                        post.can_close = is_admin or user.karma >= forum.karma_close_own
                    # Can unlink own post________________________________________________
                    if user in forum.authorized_group_unlink_own.sudo().users:
                        post.can_unlink = True
                    elif forum.karma_unlink_own == 0:
                        post.can_unlink = False
                    else:
                        post.can_unlink = is_admin or user.karma >= forum.karma_unlink_own
                    # Can comment own post________________________________________________
                    if user in forum.authorized_group_comment_own.sudo().users:
                        post.can_comment = True
                    elif forum.karma_comment_own == 0:
                        post.can_comment = False
                    else:
                        post.can_comment = is_admin or user.karma >= forum.karma_comment_own
                    # Can convert own comments______________________________________________
                    if user in forum.authorized_group_comment_convert_own.sudo().users:
                        post.can_comment_convert = True
                    elif post.karma_comment_convert == 0:
                        post.can_comment_convert = False
                    else:
                        post.can_comment_convert = is_admin or user.karma >= post.karma_comment_convert_own
                else:
                    # Can edit all posts________________________________________________
                    if user in forum.authorized_group_edit_all.sudo().users:
                        post.can_edit = True
                    elif forum.karma_edit_all == 0:
                        post.can_edit = False
                    else:
                        post.can_edit = is_admin or user.karma >= forum.karma_edit_all
                    # Can close all posts________________________________________________
                    if user in forum.authorized_group_close_all.sudo().users:
                        post.can_close = True
                    elif forum.karma_close_all == 0:
                        post.can_close = False
                    else:
                        post.can_close = is_admin or user.karma >= forum.karma_close_all
                    # Can unlink all posts________________________________________________
                    if user in forum.authorized_group_unlink_all.sudo().users:
                        post.can_unlink = True
                    elif forum.karma_unlink_all == 0:
                        post.can_unlink = False
                    else:
                        post.can_unlink = is_admin or user.karma >= forum.karma_unlink_all
                    # Can comment all posts________________________________________________
                    if user in forum.authorized_group_comment_all.sudo().users:
                        post.can_comment = True
                    elif forum.karma_comment_all == 0:
                        post.can_comment = False
                    else:
                        post.can_comment = is_admin or user.karma >= forum.karma_comment_all
                    # Can convert all comments______________________________________________
                    if user in forum.authorized_group_comment_convert_all.sudo().users:
                        post.can_comment_convert = True
                    elif forum.karma_comment_convert == 0:
                        post.can_comment_convert = False
                    else:
                        post.can_comment_convert = is_admin or user.karma >= forum.karma_comment_convert_all

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'content' in vals and vals.get('forum_id'):
                vals['content'] = self._update_content(vals['content'], vals['forum_id'])

        posts = super(Post, self.with_context(mail_create_nolog=True)).create(vals_list)

        for post in posts:
            # deleted or closed questions
            if post.parent_id and (post.parent_id.state == 'close' or post.parent_id.active is False):
                raise UserError(_('Posting answer on a [Deleted] or [Closed] question is not possible.'))
            # karma-based access
            if not post.parent_id and not post.can_ask:
                raise AccessError(_('%d karma required to create a new question.', post.forum_id.karma_ask))
            elif post.parent_id and not post.can_answer:
                raise AccessError(_('%d karma required to answer a question.', post.forum_id.karma_answer))
            if not post.parent_id and not post.can_post:
                post.sudo().state = 'pending'

            # add karma for posting new questions
            if not post.parent_id and post.state == 'active':
                post.create_uid.sudo()._add_karma(post.forum_id.karma_gen_question_new, post, _('Ask a new question'))
        posts.post_notification()
        return posts

    def write(self, vals):
        trusted_keys = ['active', 'is_correct', 'tag_ids']  # fields where security is checked manually
        if 'content' in vals:
            vals['content'] = self._update_content(vals['content'], self.forum_id.id)

        tag_ids = False
        if 'tag_ids' in vals:
            tag_ids = set(self.new({'tag_ids': vals['tag_ids']}).tag_ids.ids)

        for post in self:
            if 'state' in vals:
                if vals['state'] in ['active', 'close']:
                    if not post.can_close:
                        raise AccessError(_('%d karma required to close or reopen a post.', post.karma_close))
                    trusted_keys += ['state', 'closed_uid', 'closed_date', 'closed_reason_id']
                elif vals['state'] == 'flagged':
                    if not post.can_flag:
                        raise AccessError(_('%d karma required to flag a post.', post.forum_id.karma_flag))
                    trusted_keys += ['state', 'flag_user_id']
            if 'active' in vals:
                if not post.can_unlink:
                    raise AccessError(_('%d karma required to delete or reactivate a post.', post.karma_unlink))
            if 'is_correct' in vals:
                if not post.can_accept:
                    raise AccessError(_('%d karma required to accept or refuse an answer.', post.karma_accept))
                # update karma except for self-acceptance
                mult = 1 if vals['is_correct'] else -1
                if vals['is_correct'] != post.is_correct and post.create_uid.id != self._uid:
                    post.create_uid.sudo()._add_karma(post.forum_id.karma_gen_answer_accepted * mult, post,
                                                      _('User answer accepted') if mult > 0 else _(
                                                          'Accepted answer removed'))
                    self.env.user.sudo()._add_karma(post.forum_id.karma_gen_answer_accept * mult, post,
                                                    _('Validate an answer') if mult > 0 else _(
                                                        'Remove validated answer'))
            if tag_ids:
                if set(post.tag_ids.ids) != tag_ids and self.env.user.karma < post.forum_id.karma_edit_retag:
                    raise AccessError(_('%d karma required to retag.', post.forum_id.karma_edit_retag))
            if any(key not in trusted_keys for key in vals) and not post.can_edit:
                raise AccessError(_('%d karma required to edit a post.', post.karma_edit))

        res = super(Post, self).write(vals)

        # if post content modify, notify followers
        if 'content' in vals or 'name' in vals:
            for post in self:
                if post.parent_id:
                    body, subtype_xmlid = _('Answer Edited'), 'website_forum.mt_answer_edit'
                    obj_id = post.parent_id
                else:
                    body, subtype_xmlid = _('Question Edited'), 'website_forum.mt_question_edit'
                    obj_id = post
                obj_id.message_post(body=body, subtype_xmlid=subtype_xmlid)
        if 'active' in vals:
            answers = self.env['forum.post'].with_context(active_test=False).search([('parent_id', 'in', self.ids)])
            if answers:
                answers.write({'active': vals['active']})
        return res

    def _update_content(self, content, forum_id):
        forum = self.env['forum.forum'].browse(forum_id)
        if content and self.env.user.karma < forum.karma_dofollow:
            for match in re.findall(r'<a\s.*href=".*?">', content):
                escaped_match = re.escape(match)  # replace parenthesis or special char in regex
                url_match = re.match(r'^.*href="(.*)".*',
                                     match)  # extracting the link allows to rebuild a clean link tag
                url = url_match.group(1)
                content = re.sub(escaped_match, f'<a rel="nofollow" href="{url}">', content)

        if self.env.user.karma < forum.karma_editor:
            filter_regexp = r'(<img.*?>)|(<a[^>]*?href[^>]*?>)|(<[a-z|A-Z]+[^>]*style\s*=\s*[\'"][^\'"]*\s*background[^:]*:[^url;]*url)'
            content_match = re.search(filter_regexp, content, re.I)
            if content_match:
                raise AccessError(_('%d karma required to post an image or link.', forum.karma_editor))
        return content

    def validate(self):
        for post in self:
            if not post.can_moderate:
                raise AccessError(_('%d karma required to validate a post.', post.forum_id.karma_moderate))
            # if state == pending, no karma previously added for the new question
            if post.state == 'pending':
                post.create_uid.sudo()._add_karma(
                    post.forum_id.karma_gen_question_new,
                    post,
                    _('Ask a question'),
                )
            post.write({
                'state': 'active',
                'active': True,
                'moderator_id': self.env.user.id,
            })
            post.post_notification()
        return True

    def refuse(self):
        for post in self:
            if not post.can_moderate:
                raise AccessError(_('%d karma required to refuse a post.', post.forum_id.karma_moderate))
            post.moderator_id = self.env.user
        return True

    def flag(self):
        res = []
        for post in self:
            if not post.can_flag:
                raise AccessError(_('%d karma required to flag a post.', post.forum_id.karma_flag))
            if post.state == 'flagged':
                res.append({'error': 'post_already_flagged'})
            elif post.state == 'active':
                # TODO: potential performance bottleneck, can be batched
                post.write({
                    'state': 'flagged',
                    'flag_user_id': self.env.user.id,
                })
                res.append(
                    post.can_moderate and
                    {'success': 'post_flagged_moderator'} or
                    {'success': 'post_flagged_non_moderator'}
                )
            else:
                res.append({'error': 'post_non_flaggable'})
        return res

    def mark_as_offensive(self, reason_id):
        for post in self:
            if not post.can_moderate:
                raise AccessError(_('%d karma required to mark a post as offensive.', post.forum_id.karma_moderate))
            # remove some karma
            _logger.info('Downvoting user <%s> for posting spam/offensive contents', post.create_uid)
            post.create_uid.sudo()._add_karma(post.forum_id.karma_gen_answer_flagged, post,
                                              _('Downvote for posting offensive contents'))
            # TODO: potential bottleneck, could be done in batch
            post.write({
                'state': 'offensive',
                'moderator_id': self.env.user.id,
                'closed_date': fields.Datetime.now(),
                'closed_reason_id': reason_id,
                'active': False,
            })
        return True

    def mark_as_offensive_batch(self, key, values):
        spams = self.browse()
        if key == 'create_uid':
            spams = self.filtered(lambda x: x.create_uid.id in values)
        elif key == 'country_id':
            spams = self.filtered(lambda x: x.create_uid.country_id.id in values)
        elif key == 'post_id':
            spams = self.filtered(lambda x: x.id in values)

        reason_id = self.env.ref('website_forum.reason_8').id
        _logger.info('User %s marked as spams (in batch): %s' % (self.env.uid, spams))
        return spams.mark_as_offensive(reason_id)

    @api.ondelete(at_uninstall=False)
    def _unlink_if_enough_karma(self):
        for post in self:
            if not post.can_unlink:
                raise AccessError(_('%d karma required to unlink a post.', post.karma_unlink))

    def convert_answer_to_comment(self):
        """ Tools to convert an answer (forum.post) to a comment (mail.message).
        The original post is unlinked and a new comment is posted on the question
        using the post create_uid as the comment's author. """
        self.ensure_one()
        if not self.parent_id:
            return self.env['mail.message']

        # karma-based action check: use the post field that computed own/all value
        if not self.can_comment_convert:
            raise AccessError(_('%d karma required to convert an answer to a comment.', self.karma_comment_convert))

        # post the message
        question = self.parent_id
        self_sudo = self.sudo()
        values = {
            'author_id': self_sudo.create_uid.partner_id.id,  # use sudo here because of access to res.users model
            'email_from': self_sudo.create_uid.email_formatted,  # use sudo here because of access to res.users model
            'body': tools.html_sanitize(self.content, sanitize_attributes=True, strip_style=True, strip_classes=True),
            'message_type': 'comment',
            'subtype_xmlid': 'mail.mt_comment',
            'date': self.create_date,
        }
        # done with the author user to have create_uid correctly set
        new_message = question.with_user(self_sudo.create_uid.id).with_context(
            mail_create_nosubscribe=True).sudo().message_post(**values).sudo(False)

        # unlink the original answer, using SUPERUSER_ID to avoid karma issues
        self.sudo().unlink()

        return new_message

    @api.model
    def convert_comment_to_answer(self, message_id):
        """ Tool to convert a comment (mail.message) into an answer (forum.post).
        The original comment is unlinked and a new answer from the comment's author
        is created. Nothing is done if the comment's author already answered the
        question. """
        comment_sudo = self.env['mail.message'].sudo().browse(message_id)
        post = self.browse(comment_sudo.res_id)
        if not comment_sudo.author_id or not comment_sudo.author_id.user_ids:  # only comment posted by users can be converted
            return False

        # karma-based action check: must check the message's author to know if own / all
        is_author = comment_sudo.author_id.id == self.env.user.partner_id.id
        karma_own = post.forum_id.karma_comment_convert_own
        karma_all = post.forum_id.karma_comment_convert_all
        karma_convert = is_author and karma_own or karma_all
        can_convert = self.env.user.karma >= karma_convert
        if not can_convert:
            if is_author and karma_own < karma_all:
                raise AccessError(_('%d karma required to convert your comment to an answer.', karma_own))
            else:
                raise AccessError(_('%d karma required to convert a comment to an answer.', karma_all))

        # check the message's author has not already an answer
        question = post.parent_id if post.parent_id else post
        post_create_uid = comment_sudo.author_id.user_ids[0]
        if any(answer.create_uid.id == post_create_uid.id for answer in question.child_ids):
            return False

        # create the new post
        post_values = {
            'forum_id': question.forum_id.id,
            'content': comment_sudo.body,
            'parent_id': question.id,
            'name': _('Re: %s', question.name or ''),
        }
        # done with the author user to have create_uid correctly set
        new_post = self.with_user(post_create_uid).sudo().create(post_values).sudo(False)

        # delete comment
        comment_sudo.unlink()

        return new_post

    def unlink_comment(self, message_id):
        comment_sudo = self.env['mail.message'].sudo().browse(message_id)
        if comment_sudo.model != 'forum.post':
            return [False] * len(self)

        user_karma = self.env.user.karma
        result = []
        for post in self:
            if comment_sudo.res_id != post.id:
                result.append(False)
                continue
            # karma-based action check: must check the message's author to know if own or all
            karma_required = (
                post.forum_id.karma_comment_unlink_own
                if comment_sudo.author_id.id == self.env.user.partner_id.id
                else post.forum_id.karma_comment_unlink_all
            )
            if user_karma < karma_required:
                raise AccessError(_('%d karma required to delete a comment.', karma_required))
            result.append(comment_sudo.unlink())
        return result

    # ----------------------------------------------------------------------
    # MESSAGING
    # ----------------------------------------------------------------------

    @api.model
    def _get_mail_message_access(self, res_ids, operation, model_name=None):
        # XDO FIXME: to be correctly fixed with new _get_mail_message_access and filter access rule
        if operation in ('write', 'unlink') and (not model_name or model_name == 'forum.post'):
            # Make sure only author or moderator can edit/delete messages
            for post in self.browse(res_ids):
                if not post.can_edit:
                    raise AccessError(_('%d karma required to edit a post.', post.karma_edit))
        return super(Post, self)._get_mail_message_access(res_ids, operation, model_name=model_name)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, *, message_type='notification', **kwargs):
        if self.ids and message_type == 'comment':  # user comments have a restriction on karma
            # add followers of comments on the parent post
            if self.parent_id:
                partner_ids = kwargs.get('partner_ids', [])
                comment_subtype = self.sudo().env.ref('mail.mt_comment')
                question_followers = self.env['mail.followers'].sudo().search([
                    ('res_model', '=', self._name),
                    ('res_id', '=', self.parent_id.id),
                    ('partner_id', '!=', False),
                ]).filtered(lambda fol: comment_subtype in fol.subtype_ids).mapped('partner_id')
                partner_ids += question_followers.ids
                kwargs['partner_ids'] = partner_ids

            self.ensure_one()
            if not self.can_comment:
                raise AccessError(_('%d karma required to comment.', self.karma_comment))
            if not kwargs.get('record_name') and self.parent_id:
                kwargs['record_name'] = self.parent_id.name
        return super(Post, self).message_post(message_type=message_type, **kwargs)

    @api.model
    def _search_get_detail(self, website, order, options):
        with_description = options['displayDescription']
        with_date = options['displayDetail']
        search_fields = ['name']
        fetch_fields = ['id', 'name', 'website_url']
        mapping = {
            'name': {'name': 'name', 'type': 'text', 'match': True},
            'website_url': {'name': 'website_url', 'type': 'text', 'truncate': False},
        }

        domain = website.website_domain()
        domain = expression.AND([domain, [('state', '=', 'active'), ('can_view', '=', True)]])
        include_answers = options.get('include_answers', False)
        if not include_answers:
            domain = expression.AND([domain, [('parent_id', '=', False)]])
        forum = options.get('forum')
        if forum:
            domain = expression.AND([domain, [('forum_id', '=', unslug(forum)[1])]])
        tags = options.get('tag')
        if tags:
            domain = expression.AND([domain, [('tag_ids', 'in', [unslug(tag)[1] for tag in tags.split(',')])]])
        filters = options.get('filters')
        if filters == 'unanswered':
            domain = expression.AND([domain, [('child_ids', '=', False)]])
        elif filters == 'solved':
            domain = expression.AND([domain, [('has_validated_answer', '=', True)]])
        elif filters == 'unsolved':
            domain = expression.AND([domain, [('has_validated_answer', '=', False)]])
        user = self.env.user
        my = options.get('my')
        create_uid = user.id if my == 'mine' else options.get('create_uid')
        if create_uid:
            domain = expression.AND([domain, [('create_uid', '=', create_uid)]])
        if my == 'followed':
            domain = expression.AND([domain, [('message_partner_ids', '=', user.partner_id.id)]])
        elif my == 'tagged':
            domain = expression.AND([domain, [('tag_ids.message_partner_ids', '=', user.partner_id.id)]])
        elif my == 'favourites':
            domain = expression.AND([domain, [('favourite_ids', '=', user.id)]])
        elif my == 'upvoted':
            domain = expression.AND([domain, [('vote_ids.user_id', '=', user.id)]])

        # 'sorting' from the form's "Order by" overrides order during auto-completion
        order = options.get('sorting', order)
        if 'is_published' in order:
            parts = [part for part in order.split(',') if 'is_published' not in part]
            order = ','.join(parts)

        if with_description:
            search_fields.append('content')
            fetch_fields.append('content')
            mapping['description'] = {'name': 'content', 'type': 'text', 'html': True, 'match': True}
        if with_date:
            fetch_fields.append('write_date')
            mapping['detail'] = {'name': 'date', 'type': 'html'}
        return {
            'model': 'forum.post',
            'base_domain': [domain],
            'search_fields': search_fields,
            'fetch_fields': fetch_fields,
            'mapping': mapping,
            'icon': 'fa-comment-o',
            'order': order,
        }
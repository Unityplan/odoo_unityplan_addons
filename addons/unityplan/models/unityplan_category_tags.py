# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
from odoo import models, fields, api, _
# noinspection PyUnresolvedReferences
from odoo.exceptions import ValidationError
from random import randint


def _default_is_published():
    return True


class UnityplanCategoryTags(models.Model):
    """ Unity Plan category tags """
    _name = 'unityplan.category.tag'
    _description = 'Unity Plan Category Tags'
    _order = 'group_sequence asc, sequence asc'

    name = fields.Char(
        'Name',
        required=True,
        translate=True,
        help="The name of the category"
    )
    is_published = fields.Boolean(
        default=True,
        help="Is the category published (visible or not)"
    )
    description = fields.Text(
        'Description',
        required=True,
        translate=True,
        help="Description of the category"
    )
    sequence = fields.Integer(
        'Sequence',
        index=True
    )
    group_sequence = fields.Integer(
        'Group sequence',
        related='parent_id.sequence',
        index=True,
        store=True
    )
    child_id = fields.One2many(
        'unityplan.category.tag',
        'parent_id',
        string='Child Categories')
    parent_id = fields.Many2one(
        'unityplan.category.tag',
        string='Parent category',
        index=True,
        ondelete="restrict"
    )
    color = fields.Integer(
        string='Color Index',
        default=lambda self: randint(1, 11),
        help="Tag color used in both backend and website. No color means no display in kanban or front-end, to "
             "distinguish internal tags from public categorization tags")


    @api.constrains('parent_id')
    def _check_category_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('Error ! You cannot add the same category as a parent.'))

    def write(self, vals):
        if not self.parent_id:
            sequence = vals.get('sequence')
            if sequence is not None:
                self.group_sequence = sequence
                vals['group_sequence'] = sequence
                res = super().write(vals)
                return res
            else:
                res = super().write(vals)
                return res
        else:
            res = super().write(vals)
            return res

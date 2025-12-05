import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    restrict_group_ids = fields.Many2many(
        'res.groups', 'ir_ui_menu_group_restrict_rel', 'menu_id', 'gres_id',
        string='Groups',
        help="If you have groups, the restrict of visibility of this menu"
             " will be based on these groups.")
    hide_from_user_ids = fields.Many2many(
        'res.users', 'ir_ui_menu_res_users_hidden_rel',
        'menu_id', 'user_id', string='Hidden menus')

    
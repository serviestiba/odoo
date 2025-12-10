from odoo import models, fields, api


class Groups(models.Model):
    _inherit = "res.groups"

    menu_access_restrict = fields.Many2many(
        'ir.ui.menu', 'ir_ui_menu_group_restrict_rel',
        'gres_id', 'menu_id', string='Restrict Access Menu')
    menu_access_only = fields.Many2many(
        'ir.ui.menu', 'ir_ui_menu_group_restrict_access_only_rel',
        'gres_id', 'menu_id', string='Access Only Menus',
        help='Only selected menus will be available for this group')
    hidden_report_ids = fields.Many2many(
        'ir.actions.report', 'ir_actions_report_res_groups_hidden_reports_rel',
        'group_id', 'report_id', string='Restrict Access Reports')

    @api.model_create_multi
    def create(self, vals_list):
        return super().create(vals_list)

    def write(self, values):
        return super().write(values)

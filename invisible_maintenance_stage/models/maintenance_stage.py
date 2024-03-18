from odoo import api, fields, models


class MaintenanceStage(models.Model):
    _inherit = 'maintenance.stage'

    @api.model
    def _set_domain_group(self):
        return [("id", "in", [
            self.env.ref("invisible_maintenance_stage.maintenance_stage_column_group1").id,
            self.env.ref("invisible_maintenance_stage.maintenance_stage_column_group2").id,
        ])]

    group_id = fields.Many2one('res.groups', string='Ocultar para grupo', domain=lambda self: self._set_domain_group())

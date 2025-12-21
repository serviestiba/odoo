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


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    @api.model
    def _read_group_stage_ids(self, stages, domain, order=None):
        # NO reutilices `domain` porque es dominio de maintenance.request
        allowed_domain = [
            "|",
            ("group_id", "=", False),
            ("group_id", "in", self.env.user.group_ids.ids),
        ]
        return self.env["maintenance.stage"].search(allowed_domain, order=order)

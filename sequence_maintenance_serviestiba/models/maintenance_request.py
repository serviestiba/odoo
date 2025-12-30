from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    @api.model_create_multi
    def create(self, vals_list):
        _logger.info("Entering the overridden create method for maintenance.request")

        for vals in vals_list:
            # Solo asigna si no viene name o viene como "New" (comportamiento típico en Odoo)
            if vals.get("name", "New") in (False, "/", "New"):
                sequence = self.env["ir.sequence"].next_by_code("maintenance.request.seq")
                _logger.info("Sequence obtained: %s", sequence)

                if sequence:
                    vals["name"] = sequence
                else:
                    vals["name"] = "/"

        records = super().create(vals_list)
        _logger.info("New maintenance requests created with IDs: %s", records.ids)
        return records

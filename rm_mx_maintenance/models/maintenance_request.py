from odoo import models, fields


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    stock_picking_id = fields.One2many(
        "stock.picking",
        "maintenance_request_id",
        string="Stock Pickings",
    )

    def open_stock_picking_form(self):
        """Abrir los pickings relacionados con esta solicitud de mantenimiento."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Movimientos de Stock",
            "res_model": "stock.picking",
            "view_mode": "list,form",
            "domain": [("id", "in", self.stock_picking_id.ids)],
            "context": {
                "default_maintenance_request_id": self.id,
            },
            "target": "current",
        }


class StockPicking(models.Model):
    _inherit = "stock.picking"

    maintenance_request_id = fields.Many2one(
        "maintenance.request",
        string="Maintenance Request",
        ondelete="set null",
    )

    def assign_maintenance_request_id(self):
        """Asigna este picking a la solicitud de mantenimiento enlazada (si existe)."""
        for picking in self:
            maintenance = picking.maintenance_request_id
            if maintenance:
                maintenance.write(
                    {
                        "stock_picking_id": [(4, picking.id)],
                    }
                )

# -*- coding: utf-8 -*-

from odoo import models, fields, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    state = fields.Selection(
        selection_add=[
            ("reviewed", "Reviewed"),
            ("preapprove", "Pre Approve"),
        ]
    )

    def action_purchase_reviewed(self):
        self.write(
            {
                "state": "reviewed",
            }
        )

    def action_purchase_preapprove(self):
        self.write(
            {
                "state": "preapprove",
            }
        )

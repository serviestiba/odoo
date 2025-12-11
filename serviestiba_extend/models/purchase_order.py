# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


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

    @api.depends_context("lang")
    @api.depends(
        "order_line.tax_ids",
        "order_line.price_subtotal",
        "amount_total",
        "amount_untaxed",
    )
    def _compute_tax_totals(self):
        for order in self:
            order_lines = order.order_line.filtered(
                lambda x: not x.display_type and x.status not in ["cancel"]
            )
            order.tax_totals = 0

class ShPurchaseAgreement(models.Model):
    _inherit = "purchase.agreement"

    sh_agreement_deadline = fields.Datetime(
        String="Tender Deadline",
        tracking=True,
        default=fields.Datetime.now,
        readonly=True,
    )

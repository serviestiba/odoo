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



class ShPurchaseAgreement(models.Model):
    _inherit = "purchase.agreement"

    sh_agreement_deadline = fields.Datetime(
        String="Tender Deadline",
        tracking=True,
        default=fields.Datetime.now,
        readonly=True,
    )

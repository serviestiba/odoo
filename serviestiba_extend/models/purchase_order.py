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
        AccountTax = self.env["account.tax"]
        for order in self:
            # Filtramos las líneas que realmente cuentan para impuestos
            order_lines = order.order_line.filtered(
                lambda x: not x.display_type and x.status not in ["cancel"]
            )

            base_lines = [line._convert_to_tax_base_line_dict() for line in order_lines]

            tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=order.currency_id or order.company_id.currency_id,
                company=order.company_id,
                cash_rounding=None,  # normalmente None para compras
            )

            order.tax_totals = tax_totals


class ShPurchaseAgreement(models.Model):
    _inherit = "purchase.agreement"

    sh_agreement_deadline = fields.Datetime(
        String="Tender Deadline",
        tracking=True,
        default=fields.Datetime.now,
        readonly=True,
    )

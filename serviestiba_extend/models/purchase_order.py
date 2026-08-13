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

    @api.depends(
        "order_line.price_subtotal", "company_id", "currency_id", "order_line.status"
    )
    def _amount_all(self):
        AccountTax = self.env["account.tax"]
        for order in self:
            order_lines = order.order_line.filtered(
                lambda x: not x.display_type and not x.status == "cancel"
            )
            base_lines = [
                line._prepare_base_line_for_taxes_computation() for line in order_lines
            ]
            AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, order.company_id)
            tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=order.currency_id or order.company_id.currency_id,
                company=order.company_id,
            )
            order.amount_untaxed = tax_totals["base_amount_currency"]
            order.amount_tax = tax_totals["tax_amount_currency"]
            order.amount_total = tax_totals["total_amount_currency"]
            order.amount_total_cc = tax_totals["total_amount"]


class ShPurchaseAgreement(models.Model):
    _inherit = "purchase.agreement"

    sh_agreement_deadline = fields.Datetime(
        String="Tender Deadline",
        tracking=True,
        default=fields.Datetime.now,
        readonly=True,
    )


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _create_stock_moves(self, picking):
        values = []

        for line in self.filtered(
            lambda l: not l.display_type and l.status == "confirm"
        ):
            for val in line._prepare_stock_moves(picking):
                values.append(val)
        return self.env["stock.move"].create(values)

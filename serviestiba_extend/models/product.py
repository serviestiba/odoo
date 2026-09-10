# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import fields, models, _


CONFIRMED_LINE_DOMAIN = [("status", "=", "confirm")]


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_view_po(self):
        """Purchase History: show only Serviestiba-confirmed PO lines."""
        action = super().action_view_po()
        domain = list(action.get("domain") or [])
        if ("status", "=", "confirm") not in domain:
            domain.append(("status", "=", "confirm"))
        action["domain"] = domain
        action["display_name"] = _("Purchase History for %s", self.display_name)
        return action


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _compute_purchased_product_qty(self):
        """Count only PO lines explicitly confirmed by Serviestiba.

        Keep the same 365-day window and purchase-order-state rule used by
        Odoo 19, adding the custom line-level status == 'confirm'.
        """
        date_from = fields.Datetime.to_string(
            fields.Date.context_today(self) - relativedelta(years=1)
        )
        domain = [
            ("order_id.state", "=", "purchase"),
            ("product_id", "in", self.ids),
            ("order_id.date_approve", ">=", date_from),
            ("status", "=", "confirm"),
        ]
        order_lines = self.env["purchase.order.line"]._read_group(
            domain,
            ["product_id"],
            ["product_uom_qty:sum"],
        )
        purchased_data = {product.id: qty for product, qty in order_lines}
        for product in self:
            if not product.id:
                product.purchased_product_qty = 0.0
                continue
            product.purchased_product_qty = product.uom_id.round(
                purchased_data.get(product.id, 0.0)
            )

    def action_view_po(self):
        """Purchase History: show only Serviestiba-confirmed PO lines."""
        action = super().action_view_po()
        domain = list(action.get("domain") or [])
        if ("status", "=", "confirm") not in domain:
            domain.append(("status", "=", "confirm"))
        action["domain"] = domain
        action["display_name"] = _("Purchase History for %s", self.display_name)
        return action

# -*- coding: utf-8 -*-

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def action_view_po(self):
        """Show purchase history only for Serviestiba-confirmed PO lines."""
        action = super().action_view_po()

        # Odoo already restricts this action to confirmed purchase orders
        # (state = 'purchase') and the selected product(s).  The Serviestiba
        # customization adds a second line-level status, so only lines marked
        # as 'confirm' must be visible in Purchase History.
        domain = list(action.get("domain") or [])
        domain.append(("status", "=", "confirm"))
        action["domain"] = domain
        return action

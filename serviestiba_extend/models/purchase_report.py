# -*- coding: utf-8 -*-

from odoo import models
from odoo.tools import SQL


class PurchaseReport(models.Model):
    _inherit = "purchase.report"

    def _where(self) -> SQL:
        """Exclude Serviestibas tender lines that are not confirmed.

        ``purchase.report`` is an SQL view built from ``purchase_order_line``
        using the alias ``l`` in Odoo 19. Filtering here makes the rule apply
        consistently to Purchase Analysis pivot/graph/list and to every
        measure calculated by that report.
        """
        return SQL(
            "%s AND l.status = %s",
            super()._where(),
            "confirm",
        )

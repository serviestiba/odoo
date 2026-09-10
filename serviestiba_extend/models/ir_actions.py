# -*- coding: utf-8 -*-

from ast import literal_eval

from odoo import api, models


class IrActionsActWindow(models.Model):
    _inherit = "ir.actions.act_window"

    @api.model
    def _serviestiba_filter_confirmed_tender_lines(self):
        """Restrict Tender Lines actions to custom status == confirm.

        Softhealer can open the tender analysis with an action whose view is
        linked explicitly or only through view_mode/name.  Cover both cases,
        while limiting the change to purchase.order.line Tender Lines actions.
        """
        confirmed_filter = ("status", "=", "confirm")
        actions = self.browse()

        view = self.env.ref(
            "sh_all_in_one_tender_bundle.sh_bidline_tree_view",
            raise_if_not_found=False,
        )
        if view:
            action_views = self.env["ir.actions.act_window.view"].search([
                ("view_id", "=", view.id),
            ])
            actions |= action_views.mapped("act_window_id")

            if "view_id" in self._fields:
                actions |= self.search([
                    ("view_id", "=", view.id),
                ])

        # Some versions of the third-party module do not bind the list view
        # directly on the action.  The action is still a purchase.order.line
        # action named Tender Lines / Bid Lines / Analyze RFQ.
        actions |= self.search([
            ("res_model", "=", "purchase.order.line"),
            "|", "|",
            ("name", "ilike", "Tender Lines"),
            ("name", "ilike", "Bid Lines"),
            ("name", "ilike", "Analyze RFQ"),
        ])

        actions = actions.filtered(
            lambda action: action.res_model == "purchase.order.line"
        )

        for action in actions:
            domain = action.domain or "[]"
            if isinstance(domain, str):
                try:
                    domain = literal_eval(domain)
                except (ValueError, SyntaxError):
                    # Do not overwrite dynamic Python expressions blindly.
                    continue

            domain = list(domain or [])
            if confirmed_filter not in domain:
                domain.append(confirmed_filter)
                action.write({"domain": repr(domain)})

        return True

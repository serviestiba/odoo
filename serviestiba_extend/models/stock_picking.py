# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = "stock.picking"

    scheduled_date = fields.Datetime(
        "Scheduled Date",
        compute="_compute_scheduled_date",
        inverse="_set_scheduled_date",
        store=True,
        index=True,
        readonly=True,
        default=fields.Datetime.now,
        tracking=True,
        states={"done": [("readonly", True)], "cancel": [("readonly", True)]},
        help="Scheduled time for the first part of the shipment to be processed. Setting manually a value here would set it as expected date for all the stock moves.",
    )

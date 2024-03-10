# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class Purchase(models.Model):
    _inherit = 'purchase.order'

    is_expired = fields.Boolean(
        compute='_compute_is_expired', string="Is expired")
    signature = fields.Image('Signature', help='Signature received through the portal.',
                             copy=False, attachment=True, max_width=1024, max_height=1024)
    signed_by = fields.Char(
        'Signed By', help='Name of the person that signed the SO.', copy=False)
    signed_on = fields.Datetime(
        'Signed On', help='Date of the signature.', copy=False)

    def _compute_is_expired(self):
        today = fields.Date.today()
        for order in self:
            order.is_expired = order.state == 'sent' and order.date_order and order.date_order < today

    def has_to_be_signed(self, include_draft=False):
        return True

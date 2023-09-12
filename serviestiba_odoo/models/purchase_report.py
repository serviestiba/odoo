# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError

class PurchaseReport(models.Model):
    _inherit = 'purchase.report'

    departamento = fields.Selection(
        selection=[('TALLER', 'TALLER'),
                   ('REEFER', 'REEFER'),
                   ('OFICINA', 'OFICINA')],
        string='Departamento',
        readonly=True
        )

    def _select(self):
        return super(PurchaseReport, self)._select() + ", po.departamento as departamento"

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", po.departamento"
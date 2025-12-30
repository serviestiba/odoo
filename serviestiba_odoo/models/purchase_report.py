# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.tools.sql import SQL

class PurchaseReport(models.Model):
    _inherit = 'purchase.report'

    departamento = fields.Selection(
        selection=[
            ('TALLER', 'TALLER'),
            ('REEFER', 'REEFER'),
            ('OFICINA', 'OFICINA'),
        ],
        string='Departamento',
        readonly=True,
    )

    def _select(self):
        # super() devuelve SQL(), NO string
        return SQL("%s, po.departamento AS departamento", super()._select())

    def _group_by(self):
        # igual, debe envolverlo en SQL
        return SQL("%s, po.departamento", super()._group_by())
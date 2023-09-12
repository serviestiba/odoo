# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    departamento = fields.Selection(
        selection=[('TALLER', 'TALLER'),
                   ('REEFER', 'REEFER'),
                   ('OFICINA', 'OFICINA')],
        string='Departamento',
        )





# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Agrega una restricción SQL para evitar duplicados por nombre
    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Ya existe un producto con este nombre.'),
        ('unique_ref', 'unique(ref)', 'Ya existe un proveedor con esta referencia interna.'),
    ]
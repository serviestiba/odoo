from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Agrega una restricción SQL para evitar duplicados por nombre
    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Ya existe un proveedor con este nombre.'),
        ('unique_ref', 'unique(ref)', 'Ya existe un proveedor con esta referencia interna.'),
    ]
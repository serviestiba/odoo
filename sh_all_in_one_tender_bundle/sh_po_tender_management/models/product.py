# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class Product(models.Model):
    _inherit = 'product.product'

    sh_display_name = fields.Char(
        'Compleate Name', related='display_name', search='_search_sh_display_name')

    def _search_sh_display_name(self, operator, value):
        """Make searchable display name for import tender lines function search by product name"""
        product_ids = []
        for rec in self.search([]):
            if rec.sh_display_name and rec.sh_display_name == value:
                product_ids.append(rec.id)
        if operator == '=':
            return [('id', 'in', product_ids)]
        else:
            return []

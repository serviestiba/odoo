# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
import time
import json

class StockPicking(models.Model):
    _inherit = 'stock.move'

    maintenance_equipment_id =  fields.Many2one('maintenance.equipment', string="Equipo")


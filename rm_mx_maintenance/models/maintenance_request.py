from odoo import models, fields, api

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'
    
    stock_picking_id = fields.One2many('stock.picking', 'maintenance_request_id', string='Stock Pickings', store=True)

    def open_stock_picking_form(self):
        """
        Método para abrir el formulario de stock.picking con el contexto de la solicitud de mantenimiento actual.

        Returns:
            dict: Diccionario que describe la acción para abrir el formulario de stock.picking.
        """
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.picking',
            'view_mode': 'form',
            'target': 'new', 
            'context': {
                'default_maintenance_request_id': self.id,
            }
        }



class StockPicking(models.Model):
    _inherit = 'stock.picking'

    maintenance_request_id = fields.Many2one('maintenance.request', string='Maintenance Request')

    @api.model
    def create(self, vals):
        """
        Método para crear un nuevo registro de stock.picking.
        
        Args:
            vals (dict): Valores a utilizar para la creación del registro.

        Returns:
            res: Registro creado de stock.picking.
        """
        if 'maintenance_request_id' not in vals:
            maintenance_request_id = self._context.get('default_maintenance_request_id')
            if maintenance_request_id:
                vals['maintenance_request_id'] = maintenance_request_id
        
        res = super(StockPicking, self).create(vals)
        
        self.set_stock_picking_id(res)
        
        return res

    def set_stock_picking_id(self, res):
        """
        Método para establecer el ID de stock.picking en el campo stock_picking_id de maintenance.request.

        Args:
            res: Registro de stock.picking al que se le asignará el ID.

        Returns:
            None
        """
    
        maintenance_object = self.env['maintenance.request'].browse(res.maintenance_request_id.id)
    
        if maintenance_object:
            maintenance_object.write(
                {
                'stock_picking_id': [(4, res.id)]  
                }
            )

from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    @api.model
    def create(self, vals):
        _logger.info("Entering the overridden create method for maintenance.request")
        
        # Your custom logic here
        sequence = self.env['ir.sequence'].next_by_code('maintenance.request.seq')
        _logger.info(f"Sequence obtained: {sequence}")

        if sequence:
            vals['name'] = sequence
        elif not vals.get('name'):
            vals['name'] = '/'
        
        result = super(MaintenanceRequest, self).create(vals)
        _logger.info(f"New maintenance request created with ID: {result.id}")
        return result

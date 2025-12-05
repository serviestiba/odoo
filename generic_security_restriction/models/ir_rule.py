import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class IrRule(models.Model):
    _inherit = "ir.rule"

    @api.model
    def _compute_domain(self, model_name, mode="read"):
        """Temporalmente dejamos solo el comportamiento estándar de Odoo 19.

        La lógica de generic_security_restriction se desactiva para evitar
        problemas con el nuevo engine de dominios (fields.Domain).
        """
        return super()._compute_domain(model_name, mode=mode)

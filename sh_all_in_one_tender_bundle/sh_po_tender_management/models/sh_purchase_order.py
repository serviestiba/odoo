# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api, _


class ShPurchase(models.Model):
    _inherit = 'purchase.order'

    agreement_id = fields.Many2one('purchase.agreement', 'Purchase Tender')
    cancel_lines = fields.Boolean(
        "Cancel Lines", compute='_compute_cancel_lines', store=True)
    selected_order = fields.Boolean("Selected Orders")
    sh_msg = fields.Char("Message", compute='_compute_sh_msg')
    

    def _compute_access_url(self):
        super(ShPurchase, self)._compute_access_url()
        for order in self:
            if order.state in ['draft', 'sent']:
                order.access_url = '/my/rfq/%s' % (order.id)
            else:
                order.access_url = '/my/purchase/%s' % (order.id)

    @api.depends('partner_id')
    def _compute_sh_msg(self):
        if self:
            for rec in self:
                rec.sh_msg = ''
                if rec.agreement_id and rec.partner_id.id not in rec.agreement_id.partner_ids.ids:
                    rec.sh_msg = 'Vendor you have selected not exist in selected tender. You can still create quotation for that.'

    def _compute_cancel_lines(self):
        if self:
            for rec in self:
                if rec.state == 'cancel':
                    rec.cancel_lines = True
                else:
                    rec.cancel_lines = False


class ShPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    status = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                               ('cancel', 'Cancel')], string="State", default='draft')
    agreement_id = fields.Many2one(
        'purchase.agreement', 'Purchase Tender', related='order_id.agreement_id', store=True)
    cancel_lines = fields.Boolean(
        "Cancel Lines", related='order_id.cancel_lines', store=True)
    company_currency_id = fields.Many2one(
        'res.currency', 'Base Currency', default=lambda self: self.env.company.currency_id)
    sh_base_price_unit = fields.Monetary('Unit Price ', currency_field='company_currency_id',compute='_compute_sh_price_unit_base')
    sh_base_price_subtotal = fields.Monetary('Subtotal ', currency_field='company_currency_id',compute='_compute_sh_subtotal_base')

    def _compute_sh_price_unit_base(self):
        for rec in self:
            sh_base_price_unit = rec.order_id.currency_id._convert(
                rec.price_unit,
                rec.order_id.company_id.currency_id,
                rec.order_id.company_id,
                rec.date_order or fields.Date.today(),
            )
            rec.sh_base_price_unit = sh_base_price_unit
    
    def _compute_sh_subtotal_base(self):
        for rec in self:
            sh_base_price_subtotal = rec.order_id.currency_id._convert(
                rec.price_subtotal,
                rec.order_id.company_id.currency_id,
                rec.order_id.company_id,
                rec.date_order or fields.Date.today(),
            )
            rec.sh_base_price_subtotal = sh_base_price_subtotal

    def action_confirm(self):
        if self:
            for rec in self:
                rec.status = 'confirm'

    def action_cancel(self):
        if self:
            for rec in self:
                rec.status = 'cancel'

    def action_update_qty(self):
        if self:
            return {
                'name': _('Change Quantity'),
                'type': 'ir.actions.act_window',
                'res_model': 'update.qty',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new'
            }

# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields,_


class CreateMultiRFQ(models.TransientModel):
    _name = 'sh.create.multi.rfq'
    _description = 'Create Multiple RFQ'

    sh_partner_ids = fields.Many2many('res.partner',string='Select Vendors',required=True)
    sh_mail_template_id = fields.Many2one('mail.template',string='Email Template',domain=[('model','=','purchase.order')])

    #Declare method for create mutiple rfq from tender and send email from that rfq created
    def sh_create_and_send(self):
        """Create multiple rfq from tender based some configuration and send to vendor automatically"""
        active_tender_id = self.env['purchase.agreement'].sudo().browse(self.env.context.get('active_id'))
        if active_tender_id:
            order_ids = []
            for vendor in self.sh_partner_ids:
                line_ids = []
                current_date = None
                if active_tender_id.sh_delivery_date:
                    current_date = active_tender_id.sh_delivery_date
                else:
                    current_date = fields.Datetime.now()
                for rec_line in active_tender_id.sh_purchase_agreement_line_ids:
                    line_vals = {}
                    line_vals.update({
                        'name':rec_line.sh_product_id.name_get()[0][1],
                        'currency_id':self.env.user.partner_id.property_purchase_currency_id.id or self.env.company.currency_id.id or False,
                        'product_id': rec_line.sh_product_id.id,
                        'agreement_id': active_tender_id.id,
                        'status': 'draft',
                        'product_qty': rec_line.sh_qty,
                        'product_uom': rec_line.sh_product_id.uom_id.id,
                        'price_unit': 0.0,
                        'date_planned':current_date,
                        'state':'sent'
                    })
                    line_ids.append((0, 0, line_vals))
                po_vals={
                    'partner_id':vendor.id,
                    'agreement_id':active_tender_id.id,
                    'user_id':self.env.user.id,
                    'order_line': line_ids,
                }
                order_id = self.env['purchase.order'].sudo().create(po_vals)
                order_id.state = 'sent'
                order_ids.append(order_id.id)
                if order_id:
                    self.sh_mail_template_id.sudo().send_mail(order_id.id, force_send=True)
            if order_ids:
                return {
                    'name': _('Request For Quotations'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'purchase.order',
                    'view_mode': 'tree,form',
                    'domain':[('id','in',order_ids)],
                    'target': 'current'
                }

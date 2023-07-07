# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields,api, _


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def action_send_mail(self):
        """Override method for add vendor as follower while send tender by email"""
        super(MailComposeMessage, self).action_send_mail()
        if self.env.context.get('active_model') == 'purchase.agreement' and self.env.context.get('active_id'):
            tender_id = self.env['purchase.agreement'].sudo().browse(self.env.context.get('active_id'))
            if tender_id and self.partner_ids and self.env.company.sh_auto_add_followers:
                tender_id.message_subscribe(self.partner_ids.ids)


class ShPurchaseAgreement(models.Model):
    _name = 'purchase.agreement'
    _description = 'Purchase Agreement'
    _rec_name = 'name'
    _inherit = ['portal.mixin', 'mail.thread',
                'mail.activity.mixin', 'utm.mixin']

    name = fields.Char('Name', readonly=True, tracking=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('bid_selection', 'Bid Selection'), (
        'closed', 'Closed'), ('cancel', 'Cancelled')], string="State", default='draft', tracking=True)
    rfq_count = fields.Integer("Received Quotations", compute='_compute_rfq_count')
    order_count = fields.Integer("Selected Orders", compute='_compute_order_count')
    sh_purchase_user_id = fields.Many2one(
        'res.users', 'Purchase Representative', tracking=True,domain=[('share','=',False)])
    sh_agreement_type = fields.Many2one(
        'purchase.agreement.type', 'Tender Type', required=True, tracking=True)
    sh_vender_id = fields.Many2one(
        'res.partner', 'Vendor', tracking=True)
    partner_id = fields.Many2one('res.partner', 'Partner')
    partner_ids = fields.Many2many(
        'res.partner', string='Vendors', tracking=True,domain=[('supplier_rank','>',0)])
    user_id = fields.Many2one('res.users', 'User')
    sh_agreement_deadline = fields.Datetime(
        'Tender Deadline', tracking=True)
    sh_order_date = fields.Date('Ordering Date', tracking=True)
    sh_delivery_date = fields.Date(
        'Delivery Date', tracking=True)
    sh_source = fields.Char('Source Document', tracking=True)
    sh_notes = fields.Text("Terms & Conditions", tracking=True)
    sh_purchase_agreement_line_ids = fields.One2many(
        'purchase.agreement.line', 'agreement_id', string='Purchase Agreement Line')
    company_id = fields.Many2one(
        'res.company', string='Company', required=True, default=lambda self: self.env.company)
    compute_custom_boolean = fields.Boolean(compute='_compute_module_boolean')
    sh_manage_tender_document = fields.Boolean(compute='_compute_tender_document')
    document_count = fields.Integer('Documents',compute='_compute_documents')

    @api.onchange('sh_agreement_type')
    def onchange_sh_agreement_type(self):
        """Get and set call for tender note based on purchase type"""
        self.ensure_one()
        if self.sh_agreement_type.note:
            self.sh_notes = self.sh_agreement_type.note

    def _compute_tender_document(self):
        """Set Config for tender document smart button will visible or not"""
        for rec in self:
            rec.sh_manage_tender_document = False
            if self.env.company.sh_tender_document_manage:
                rec.sh_manage_tender_document = True

    def _compute_documents(self):
        """Compute Tender Document count as attached in the tender"""
        for rec in self:
            rec.document_count = 0
            attachment_ids = self.env['ir.attachment'].sudo().search([('res_model','=','purchase.agreement'),('res_id','=',rec.id)])
            if attachment_ids:
                rec.document_count = len(attachment_ids.ids)

    def action_view_documents(self):
        """Tender Document smart button method for view all tender related document"""
        self.ensure_one()
        return {
            'name':'Tender Documents',
            'type':'ir.actions.act_window',
            'res_model':'ir.attachment',
            'view_mode':'kanban,tree,form',
            'domain':[('res_model','=','purchase.agreement'),('res_id','=',self.id)],
            'target':'current',
            }

    def _compute_module_boolean(self):
        if self:
            for rec in self:
                rec.compute_custom_boolean = False
                portal_module_id = self.env['ir.module.module'].sudo().search(
                    [('name', '=', 'sh_po_tender_portal'), ('state', 'in', ['installed'])], limit=1)
                if portal_module_id:
                    rec.compute_custom_boolean = True

    def _compute_access_url(self):
        """Set Portal Access url"""
        super(ShPurchaseAgreement, self)._compute_access_url()
        for tender in self:
            tender.access_url = '/my/tender/%s' % (tender.id)

    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s %s' % ('Tender', self.name)

    def _compute_rfq_count(self):
        """Compute Tender Related RFQ"""
        if self:
            for rec in self:
                purchase_orders = self.env['purchase.order'].sudo().search(
                    [('agreement_id', '=', rec.id), ('state', 'in', ['draft','sent'])])
                if purchase_orders:
                    rec.rfq_count = len(purchase_orders.ids)
                else:
                    rec.rfq_count = 0

    def _compute_order_count(self):
        """Compute Purchase order count which are selected based on analysis"""
        if self:
            for rec in self:
                purchase_orders = self.env['purchase.order'].sudo().search(
                    [('agreement_id', '=', rec.id), ('state', 'in', ['purchase','done'])])
                if purchase_orders:
                    rec.order_count = len(purchase_orders.ids)
                else:
                    rec.order_count = 0

    def action_confirm(self):
        """Update sequence and state changed to confirm"""
        if self:
            for rec in self:
                if rec.company_id:
                    self = self.with_company(rec.company_id.id)
                rec.name = self.env['ir.sequence'].next_by_code('purchase.agreement') or _('New')
                rec.state = 'confirm'

    def action_new_quotation(self):
        """Create New RFQ based on click button"""
        if self:
            for rec in self:
                line_ids = []
                current_date = None
                if rec.sh_delivery_date:
                    current_date = rec.sh_delivery_date
                else:
                    current_date = fields.Datetime.now()
                for rec_line in rec.sh_purchase_agreement_line_ids:
                    line_vals = {
                        'product_id': rec_line.sh_product_id.id,
                        'name': rec_line.sh_product_id.name,
                        'date_planned': current_date,
                        'product_qty': rec_line.sh_qty,
                        'status': 'draft',
                        'agreement_id': rec.id,
                        'product_uom': rec_line.sh_product_id.uom_id.id,
                        'price_unit': rec_line.sh_price_unit,
                    }
                    line_ids.append((0, 0, line_vals))
                return {
                    'name': _('New'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'purchase.order',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'context': {'default_notes':rec.sh_notes or '','default_agreement_id': rec.id, 'default_user_id': rec.sh_purchase_user_id.id, 'default_order_line': line_ids},
                    'target': 'current'
                }

    def action_validate(self):
        """Create Vendor as portal user and state change to Bid Selection"""
        if self:
            for rec in self:
                if self.env.company.sh_auto_add_followers and rec.partner_ids:
                    rec.message_subscribe(rec.partner_ids.ids)
                if self.env.company.sh_portal_user_create and rec.partner_ids:
                    for vendor in rec.partner_ids:
                        user_id = self.env['res.users'].sudo().search([('partner_id','=',vendor.id)],limit=1)
                        if not user_id:
                            portal_wizard_obj = self.env['portal.wizard']
                            created_portal_wizard =  portal_wizard_obj.create({})
                            if created_portal_wizard and vendor.email and self.env.user:
                                portal_wizard_user_obj = self.env['portal.wizard.user']
                                wiz_user_vals = {
                                    'wizard_id': created_portal_wizard.id,
                                    'partner_id': vendor.id,
                                    'email' : vendor.email,
                                    'is_portal' : True,
                                    'user_id' : self.env.user.id,
                                    }
                                created_portal_wizard_user = portal_wizard_user_obj.create(wiz_user_vals)
                                created_portal_wizard_user.action_grant_access()
                                if created_portal_wizard_user:
                                    # created_portal_wizard.action_open_wizard()
                                    vendor_portal_user_id = self.env['res.users'].sudo().search([('partner_id','=',vendor.id)],limit=1)
                                    if vendor_portal_user_id:
                                        vendor_portal_user_id.is_tendor_vendor = True
                rec.state = 'bid_selection'

    def action_analyze_rfq(self):
        """Goes to analysis of tender (purchase order line) view."""
        list_id = self.env.ref(
            'sh_all_in_one_tender_bundle.sh_bidline_tree_view').id
        form_id = self.env.ref(
            'sh_all_in_one_tender_bundle.sh_bidline_form_view').id
        pivot_id = self.env.ref(
            'sh_all_in_one_tender_bundle.purchase_order_line_pivot_custom').id
        return {
            'name': _('Tender Lines'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order.line',
            'view_type': 'form',
            'view_mode': 'tree,pivot,form',
            'views': [(list_id, 'tree'), (pivot_id, 'pivot'), (form_id, 'form')],
            'domain': [('agreement_id', '=', self.id), ('state', 'not in', ['cancel']), ('order_id.selected_order', '=', False)],
            'context': {'search_default_groupby_product': 1},
            'target': 'current'
        }

    def action_set_to_draft(self):
        """Set To Draft as tender"""
        if self:
            for rec in self:
                rec.state = 'draft'

    def action_close(self):
        """Method for closed tender"""
        if self:
            for rec in self:
                rec.state = 'closed'

    def action_cancel(self):
        """Method for cancel tender in case not proper tender data"""
        if self:
            for rec in self:
                rec.state = 'cancel'

    def action_send_tender(self):
        """Send tender to selected vendors"""
        self.ensure_one()
        template_id = self.env.ref('sh_all_in_one_tender_bundle.email_template_edi_purchase_tedner')
        ctx = {
            'default_model': 'purchase.agreement',
            'default_res_id': self.ids[0],
            'default_template_id': template_id.id,
            'default_composition_mode': 'comment',
            'force_email': True
        }
        if self.sh_vender_id:
            ctx.update({
                'default_partner_ids': [(6, 0, self.sh_vender_id.ids)]
            })
        if self.partner_ids:
            ctx.update({
                'default_partner_ids': [(6, 0, self.partner_ids.ids)]
            })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def action_view_quote(self):
        """Received Quotation smart button method for view RFQ's"""
        return {
            'name': _('Received Quotations'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('agreement_id', '=', self.id), ('selected_order', '=', False), ('state', 'in', ['draft','sent'])],
            'target': 'current'
        }

    def action_view_order(self):
        """Received Quotation smart button method for view selected Orders"""
        return {
            'name': _('Selected Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [('agreement_id', '=', self.id),('state', 'in', ['done','purchase'])],
            'target': 'current'
        }

    def action_purchase_tender_xls(self):
        """Print XLS reports"""
        return {
            'name':
            'Export Xls',
            'res_model':
            'purchase.agreement.xls.report',
            'view_mode':
            'form',
            'context': {
                'default_parent_record': self.id
            },
            'view_id':
            self.env.ref(
                'sh_all_in_one_tender_bundle.purchase_agreement_xls_report_view_form'
            ).id,
            'target':
            'new',
            'type':
            'ir.actions.act_window'
        }

    def sh_action_create_multiple_rfq(self):
        """Open Create multi rfq popup for multiple vendors"""
        self.ensure_one()
        return {
            'name': _('Create Multiple RFQ From Tender'),
            'type': 'ir.actions.act_window',
            'res_model': 'sh.create.multi.rfq',
            'view_mode': 'form',
            'context':{'default_sh_partner_ids':[(6,0,self.partner_ids.ids or [])],'default_sh_mail_template_id':self.env.ref('purchase.email_template_edi_purchase').id or False},
            'target': 'new'
        }

    def action_import_tl(self):
        """Open Import Tender Lines popup"""
        self.ensure_one()
        return {
            'name': _('Import Tender Lines'),
            'type': 'ir.actions.act_window',
            'res_model': 'sh.import.tender.lines',
            'view_mode': 'form',
            'target': 'new'
        }

class ShPurchaseAgreementLine(models.Model):
    _name = 'purchase.agreement.line'
    _description = "Purchase Agreement Line"

    agreement_id = fields.Many2one('purchase.agreement', 'Purchase Tender')
    sh_product_id = fields.Many2one(
        'product.product', 'Product', required=True)
    sh_qty = fields.Float('Quantity', default=1.0)
    sh_ordered_qty = fields.Float(
        'Ordered Quantities', compute='_compute_ordered_qty')
    sh_price_unit = fields.Float('Unit Price')
    company_id = fields.Many2one('res.company', related='agreement_id.company_id',
                                 string='Company', store=True, readonly=True, default=lambda self: self.env.company)

    def _compute_ordered_qty(self):
        """Compute Received Quantities as ordered qty in tender line"""
        if self:
            for rec in self:
                order_qty = 0.0
                purchase_order_lines = self.env['purchase.order.line'].sudo().search([('product_id', '=', rec.sh_product_id.id), (
                    'agreement_id', '=', rec.agreement_id.id), ('order_id.selected_order', '=', True), ('order_id.state', 'in', ['purchase'])])
                for line in purchase_order_lines:
                    order_qty += line.product_qty
                rec.sh_ordered_qty = order_qty

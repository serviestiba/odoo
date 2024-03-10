# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields, api
from datetime import timedelta


class Attachment(models.Model):
    _inherit = 'ir.attachment'

    sh_is_publish_in_portal = fields.Boolean('Publish in tender portal ?')
    sh_document_from_portal = fields.Boolean('Documents from portal')


class PurchaseAgreement(models.Model):
    _inherit = 'purchase.agreement'

    sh_allow_portal_access = fields.Boolean('Allow Portal Access ?')
    sh_time_limit = fields.Integer('Time Limit')
    sh_last_date_of_portal_access = fields.Date('Last date of portal access')
    sh_open_tender = fields.Boolean('Open Tender ?')
    sh_do_not_show_to_ids = fields.Many2many('res.partner','contact_id',string="Do not show to")
    sh_take_document_to_rfq = fields.Boolean('Take Tender Document To RFQ')

    def _compute_access_url(self):
        super(PurchaseAgreement, self)._compute_access_url()
        for tender in self:
            if tender.sh_open_tender:
                tender.access_url = '/my/open_tender/%s' % (tender.id)
            else:
                tender.access_url = '/my/tender/%s' % (tender.id)

    @api.onchange('sh_last_date_of_portal_access')
    def onchange_sh_last_date_of_portal_access(self):
        self.ensure_one()
        if self.sh_last_date_of_portal_access:
            delta = self.sh_last_date_of_portal_access - fields.Date.today()
            self.sh_time_limit = delta.days
        if self.sh_last_date_of_portal_access and self.sh_last_date_of_portal_access < fields.Date.today():
            self.sh_allow_portal_access = False

    @api.onchange('sh_allow_portal_access','sh_time_limit')
    def onchange_sh_time_limit(self):
        self.ensure_one()
        if self.sh_allow_portal_access:
            self.sh_last_date_of_portal_access = fields.Date.today() + timedelta(days=self.sh_time_limit)
        else:
            self.sh_last_date_of_portal_access = False
    
    @api.model
    def _run_auto_deactivate_tender_portal_access(self):
        tenders = self.env['purchase.agreement'].sudo().search([('sh_allow_portal_access','=',True),('sh_last_date_of_portal_access','!=',False)])
        if tenders:
            for tender in tenders:
                if tender.sh_last_date_of_portal_access == fields.Date.today():
                    tender.sh_allow_portal_access = False
                    tender.sh_last_date_of_portal_access = False

    @api.model
    def _run_auto_delete_tender_zip_files(self):
        attachment_ids = self.env['ir.attachment'].sudo().search([('sh_document_from_portal','=',True)])
        if attachment_ids:
            attachment_ids.sudo().unlink()

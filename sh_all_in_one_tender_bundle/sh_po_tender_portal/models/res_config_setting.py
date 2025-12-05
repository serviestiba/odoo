# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields


class Company(models.Model):
    _inherit = 'res.company'

    sh_manage_tender_doc_portal = fields.Boolean('Manage Portal Tender Document ?')
    sh_notify_purchase_representative_po = fields.Boolean('Notify Purchase Buyer while update bid from portal')
    sh_notify_purchase_representative = fields.Boolean('Notify Purchase Representative Of Tender while update bid from portal')


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    sh_manage_tender_doc_portal = fields.Boolean('Manage Portal Tender Document ?',related='company_id.sh_manage_tender_doc_portal',readonly=False)
    sh_notify_purchase_representative_po = fields.Boolean('Notify Purchase Buyer while update bid from portal',related='company_id.sh_notify_purchase_representative_po',readonly=False)
    sh_notify_purchase_representative = fields.Boolean('Notify Purchase Representative Of Tender while update bid from portal',related='company_id.sh_notify_purchase_representative',readonly=False)
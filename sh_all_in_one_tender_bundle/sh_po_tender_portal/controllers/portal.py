# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import json
import base64
from werkzeug.utils import redirect
import io
import os
import zipfile
from io import BytesIO
import tempfile
import shutil
from odoo.exceptions import UserError,AccessError, MissingError
from odoo.tools import ustr


class TenderPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        tender_obj = request.env['purchase.agreement']
        if request.env.user.is_tendor_vendor:
            if request.env.user.has_group('sh_po_tender_management.sh_purchase_tender_user'):
                tender_count = tender_obj.sudo().search_count([('sh_open_tender','=',False),('state', 'not in', ['draft'])])
                values['tender_count'] = tender_count
                return values
            else:
                tender_count = tender_obj.sudo().search_count([('sh_open_tender','=',False),('state', 'not in', ['draft']), (
                    'partner_ids', 'in', [request.env.user.partner_id.id])])
                values['tender_count'] = tender_count
        return values

    def _prepare_portal_layout_values(self):
        """Prepare Portal Home values for My Account page at portal"""
        values = super(TenderPortal, self)._prepare_portal_layout_values()
        tender_obj = request.env['purchase.agreement']
        if request.env.user.has_group('sh_po_tender_management.sh_purchase_tender_user'):
            tenders = tender_obj.sudo().search([('sh_open_tender','=',False),('state', 'not in', ['draft'])])
            tender_count = tender_obj.sudo().search_count([('sh_open_tender','=',False),('state', 'not in', ['draft'])])
            values['tender_count'] = tender_count
            values['tenders'] = tenders
            return values
        else:
            tenders = tender_obj.sudo().search([('sh_open_tender','=',False),('state', 'not in', ['draft']), (
                'partner_ids', 'in', [request.env.user.partner_id.id])])
            tender_count = tender_obj.sudo().search_count([('sh_open_tender','=',False),('state', 'not in', ['draft']), (
                'partner_ids', 'in', [request.env.user.partner_id.id])])
            values['tender_count'] = tender_count
            values['tenders'] = tenders
            return values

    @http.route(['/my/tender', '/my/tender/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_home_tender(self, page=1):
        values = self._prepare_portal_layout_values()
        tender_obj = request.env['purchase.agreement']
        domain = [
            ('sh_open_tender','=',False),
            ('state', 'not in', ['draft']),
        ]
        if not request.env.user.has_group('sh_all_in_one_tender_bundle.sh_purchase_tender_user'):
            domain.append(('partner_ids', 'in', [request.env.user.partner_id.id]))

        searchbar_filters = {}
        if not request.env.user.has_group('sh_all_in_one_tender_bundle.sh_purchase_tender_user') or not request.env.user.has_group('sh_all_in_one_tender_bundle.sh_purchase_tender_manager'):
            searchbar_filters.update({
                'all': {'label': _('All'), 'domain': [('sh_open_tender','=',False),('state', 'in', ['confirm','bid_selection']), ('partner_ids', 'in', [request.env.user.partner_id.id])]},
                'draft': {'label': _('Closed'), 'domain': [('sh_open_tender','=',False),('state', '=', 'closed'), ('partner_ids', 'in', [request.env.user.partner_id.id])]},
                'cancel': {'label': _('Cancelled'), 'domain': [('sh_open_tender','=',False),('state', '=', ['cancel']), ('partner_ids', 'in', [request.env.user.partner_id.id])]},
            })
        else:
            searchbar_filters.update({
                'all': {'label': _('All'), 'domain': [('sh_open_tender','=',False),('state', 'in', ['confirm','bid_selection'])]},
                'draft': {'label': _('Closed'), 'domain': [('sh_open_tender','=',False),('state', '=', 'closed')]},
                'cancel': {'label': _('Cancelled'), 'domain': [('sh_open_tender','=',False),('state', '=', ['cancel'])]},
            })
        # default filter by value
        tender_count = tender_obj.sudo().search_count(domain)

        pager = portal_pager(
            url="/my/tender",
            total=tender_count,
            page=page,
            step=self._items_per_page
        )

        tenders = tender_obj.sudo().search(
            domain, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'tenders': tenders,
            'page_name': 'tender',
            'pager': pager,
            'default_url': '/my/tender',
            'tender_count': tender_count,
        })
        return request.render("sh_all_in_one_tender_bundle.portal_my_tenders", values)

    @http.route(['/my/tender/<int:tender_id>'], type='http', auth="user", website=True)
    def portal_my_tender_form(self, tender_id, report_type=None, access_token=None, message=False, download=False, **kw):
        tender = request.env['purchase.agreement'].sudo().browse(tender_id)
        try:
            if not request.env.user.has_group('sh_all_in_one_tender_bundle.sh_purchase_tender_user'):
                if tender.sh_open_tender:
                    if tender.sh_do_not_show_to_ids and request.env.user.partner_id.id in tender.sh_do_not_show_to_ids.ids:
                        return request.redirect('/my')
                    elif tender.sh_do_not_show_to_ids and request.env.user.partner_id.id not in tender.sh_do_not_show_to_ids.ids:
                        if tender.sh_allow_portal_access:
                            tender_sudo = self._document_check_access('purchase.agreement', tender_id, access_token=access_token)
                        else:
                            tender_sudo = self._document_check_access('purchase.agreement', tender_id, access_token=None)        
                else:
                    if tender.sh_allow_portal_access:
                        if tender.partner_ids and request.env.user.partner_id.id in tender.partner_ids.ids:
                            tender_sudo = self._document_check_access('purchase.agreement', tender_id, access_token=access_token)
                        elif tender.partner_ids and request.env.user.partner_id.id not in tender.partner_ids.ids:
                            if access_token:
                                tender_sudo = self._document_check_access('purchase.agreement', tender_id, access_token=access_token)
                            else:
                                return request.redirect('/my')        
                    else:
                        if tender.partner_ids:
                            if request.env.user.partner_id.id in tender.partner_ids.ids:
                                tender_sudo = self._document_check_access('purchase.agreement', tender_id, access_token=None)
                            elif request.env.user.partner_id.id not in tender.partner_ids.ids:
                                return request.redirect('/my')
                        else:
                            return request.redirect('/my')
                    
        except (AccessError, MissingError):
            return request.redirect('/my')
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=tender, report_type=report_type, report_ref='sh_all_in_one_tender_bundle.action_report_purchase_tender', download=download)
        if report_type == 'sh_po_tender_portal_xls':
            return self.sh_po_tender_portal_xls(tender)
        values = {
            'token': access_token,
            'tender': tender,
            'message': message,
            'bootstrap_formatting': True,
            'partner_id': tender.partner_id.id,
            'report_type': 'html',
        }
        return request.render('sh_all_in_one_tender_bundle.portal_tender_form_template', values)
    
    def sh_po_tender_portal_xls(self, tender):
        if tender:
            get_wizard_id = request.env[
                'purchase.agreement.xls.report'].sudo().create({
                    'parent_record':
                    tender.id,
                    'report_select':
                    'purchase_tender'
                })
            report_action = get_wizard_id.get_xls_reports()
            url = report_action.get('url')
            return request.redirect(url)

    @http.route(['/rfq/create'], type='json', auth='user', website=True, csrf=False)
    def portal_create_rfq(self, **kw):
        """Create RFQ from Tender Views based on Add/Update Bid button from tender portal list and form view"""
        dic = {}
        purchase_tender = request.env['purchase.agreement'].sudo().search(
            [('id', '=', int(kw.get('tender_id')))], limit=1)

        purchase_order = request.env['purchase.order'].sudo().search(
            [('agreement_id', '=', purchase_tender.id), ('partner_id', '=', request.env.user.partner_id.id), ('state', 'in', ['draft'])])
        if purchase_order and len(purchase_order.ids) > 1:
            dic.update({
                'url': '/my/rfq'
            })
        elif purchase_order and len(purchase_order.ids) == 1:
            dic.update({
                'url': '/my/rfq/'+str(purchase_order.id)
            })
        else:
            order_dic = {}
            order_dic.update({
                'partner_id': request.env.user.partner_id.id,
                'agreement_id': purchase_tender.id,
                'date_order': fields.Datetime.now(),
                'user_id': purchase_tender.sh_purchase_user_id.id,
                'state': 'draft',
            })
            if purchase_tender.sh_notes:
                order_dic.update({
                    'notes':purchase_tender.sh_notes
                })
            if purchase_tender.sh_agreement_deadline:
                order_dic.update({
                    'date_planned': purchase_tender.sh_agreement_deadline,
                })
            else:
                order_dic.update({
                    'date_planned': fields.Datetime.now(),
                })
            purchase_order_id = request.env['purchase.order'].sudo().create(
                order_dic)
            line_ids = []
            for line in purchase_tender.sh_purchase_agreement_line_ids:
                line_vals = {
                    'order_id': purchase_order_id.id,
                    'product_id': line.sh_product_id.id,
                    'agreement_id': purchase_tender.id,
                    'status': 'draft',
                    'name': line.sh_product_id.name,
                    'product_qty': line.sh_qty,
                    'product_uom': line.sh_product_id.uom_id.id,
                    'price_unit': 0.0,
                }
                if purchase_tender.sh_agreement_deadline:
                    line_vals.update({
                        'date_planned': purchase_tender.sh_agreement_deadline,
                    })
                else:
                    line_vals.update({
                        'date_planned': fields.Datetime.now(),
                    })
                line_ids.append((0, 0, line_vals))
            purchase_order_id.order_line = line_ids
            if purchase_order_id and purchase_tender and purchase_tender.sh_take_document_to_rfq:
                attachment_ids = request.env['ir.attachment'].sudo().sudo().search([('res_model','=','purchase.agreement'),('res_id','=',purchase_tender.id),('sh_is_publish_in_portal','=',True)])
                if attachment_ids:
                    for attachment in attachment_ids:
                        attachment_vals = {
                            'name': attachment.name,
                            'datas': attachment.datas,
                            'type': attachment.type,
                            'mimetype': attachment.mimetype,
                            'store_fname': attachment.store_fname,
                            'res_model': 'purchase.order',
                            'sh_is_publish_in_portal':True,
                            'res_id': purchase_order_id.id,
                        }
                        if attachment_vals:
                            request.env['ir.attachment'].sudo().create(attachment_vals)


            dic.update({
                'url': '/my/rfq/'+str(purchase_order_id.id)
            })
        return dic

    @http.route(['/attachment/download', ], type='http', auth='user')
    def download_file(self, attachment_id):
        # Check if this is a valid attachment id
        attachment = request.env['ir.attachment'].sudo().search_read(
            [('id', '=', int(attachment_id))],
            ["name", "datas", "res_model", "res_id", "type", "url"]
        )
        if attachment:
            attachment = attachment[0]
        if attachment["type"] == "url":
            if attachment["url"]:
                return redirect(attachment["url"])
            else:
                return request.not_found()
        elif attachment["datas"]:
            data = io.BytesIO(base64.standard_b64decode(attachment["datas"]))
            return http.send_file(data, filename=attachment['name'], as_attachment=True)
        else:
            return request.not_found()

    @http.route(['/rfq/all/document/download', ], type='http', auth='public')
    def po_portal_all_document_download(self,attachment_ids):
        return self.po_document_download_all(attachment_ids)
    
    def po_document_download_all(self, get_attachment):
        try:
            mem_zip = BytesIO()
            tmp_dir = tempfile.mkdtemp(suffix=None, prefix=None, dir=None)
            path = tmp_dir
            path_main = os.path.join('/tmp', 'Tender Documents')
            is_exist = os.path.exists(path_main)
            if not is_exist:
                os.mkdir(path_main)
            path_ED = path_main
            path_ID = tmp_dir
            document_category_id = False
            with zipfile.ZipFile(mem_zip,
                                 mode="w",
                                 compression=zipfile.ZIP_DEFLATED) as zf:
                res = get_attachment.strip('][').split(', ')
                documents = []
                for elem in res:
                    documents.append(int(elem))
                tender_attachments = request.env['ir.attachment'].sudo().browse(documents)
                if tender_attachments:
                    for attachment in tender_attachments:
                        # if bill then only export attachment.
                        attachment_name = attachment.name.replace(
                            '/', '_') if attachment.name else 'attachment'
                        f = open(path + "/" + attachment_name, "wb")  # create
                        content_base64 = base64.b64decode(attachment.datas)
                        f.write(content_base64)
                        f.close()
                        zf.write(path + "/" + attachment_name)
            content = base64.encodebytes(mem_zip.getvalue())
            if content:
                attachment_id = request.env['ir.attachment'].sudo().create({
                    'name':
                    'Tender Documents' + '.zip',
                    'sh_document_from_portal':True,
                    'type':
                    'binary',
                    'mimetype':
                    'application/zip',
                    'datas':
                    content
                })
                shutil.rmtree(tmp_dir)
                token = attachment_id.generate_access_token()[0]

                url = "/web/content?model=ir.attachment&id=" + str(
                    attachment_id.id
                ) + "&field=datas&download=true&filename=" + attachment_id.name + '&access_token=' + str(
                    token)
                return redirect(url)
        except Exception as e:
            raise UserError(_("Something went wrong! " + ustr(e)))

class OpenTenderPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        tender_obj = request.env['purchase.agreement']
        if request.env.user.is_tendor_vendor:
            if not request.env.user.has_group('sh_po_tender_management.sh_purchase_tender_user'):
                open_tender_count = tender_obj.sudo().search_count([('sh_open_tender','=',True),('sh_do_not_show_to_ids','not in',[request.env.user.partner_id.id]),('state', 'not in', ['draft'])])
                values['open_tender_count'] = open_tender_count
                return values
            else:
                open_tender_count = tender_obj.sudo().search_count([('sh_open_tender','=',True),('state', 'not in', ['draft'])])
                values['open_tender_count'] = open_tender_count
                return values
        return values

    def _prepare_portal_layout_values(self):
        """Prepare Home Values display in my account page"""
        values = super(OpenTenderPortal, self)._prepare_portal_layout_values()
        tender_obj = request.env['purchase.agreement']
        if not request.env.user.has_group('sh_po_tender_management.sh_purchase_tender_user'):
            open_tenders = tender_obj.sudo().search([('sh_open_tender','=',True),('sh_do_not_show_to_ids','not in',[request.env.user.partner_id.id]),('state', 'not in', ['draft'])])
            open_tender_count = tender_obj.sudo().search_count([('sh_open_tender','=',True),('sh_do_not_show_to_ids','not in',[request.env.user.partner_id.id]),('state', 'not in', ['draft'])])
            values['open_tender_count'] = open_tender_count
            values['open_tenders'] = open_tenders
            return values
        else:
            open_tenders = tender_obj.sudo().search([('sh_open_tender','=',True),('state', 'not in', ['draft'])])
            open_tender_count = tender_obj.sudo().search_count([('sh_open_tender','=',True),('state', 'not in', ['draft'])])
            values['open_tender_count'] = open_tender_count
            values['open_tenders'] = open_tenders
            return values

    @http.route(['/my/open_tender', '/my/open_tender/page/<int:page>'], type='http', auth="user", website=True)
    def open_portal_my_home_tender(self, page=1):
        values = self._prepare_portal_layout_values()
        tender_obj = request.env['purchase.agreement']
        domain = [
            ('sh_open_tender','=',True),
            ('state', 'not in', ['draft']),
        ]
        if not request.env.user.has_group('sh_all_in_one_tender_bundle.sh_purchase_tender_user'):
            domain.append(('sh_do_not_show_to_ids','not in',[request.env.user.partner_id.id]))
        searchbar_filters={}
        if not request.env.user.has_group('sh_all_in_one_tender_bundle.sh_purchase_tender_user') or not request.env.user.has_group('sh_all_in_one_tender_bundle.sh_purchase_tender_manager'):
            searchbar_filters.update({
                'all': {'label': _('All'), 'domain': [('sh_open_tender','=',True),('sh_do_not_show_to_ids','not in',[request.env.user.partner_id.id]),('state', 'in', ['confirm','bid_selection'])]},
                'draft': {'label': _('Closed'), 'domain': [('sh_open_tender','=',True),('state', '=', 'closed'), ('sh_do_not_show_to_ids','not in',[request.env.user.partner_id.id])]},
                'cancel': {'label': _('Cancelled'), 'domain': [('sh_open_tender','=',True),('state', '=', ['cancel']), ('sh_do_not_show_to_ids','not in',[request.env.user.partner_id.id])]},
            })
        else:
            searchbar_filters.update({
                'all': {'label': _('All'), 'domain': [('sh_open_tender','=',True),('state', 'in', ['confirm','bid_selection'])]},
                'draft': {'label': _('Closed'), 'domain': [('sh_open_tender','=',True),('state', '=', 'closed')]},
                'cancel': {'label': _('Cancelled'), 'domain': [('sh_open_tender','=',True),('state', '=', ['cancel'])]},
            })
        
        open_tender_count = tender_obj.sudo().search_count(domain)

        pager = portal_pager(
            url="/my/open_tender",
            total=open_tender_count,
            page=page,
            step=self._items_per_page
        )

        open_tenders = tender_obj.sudo().search(
            domain, limit=self._items_per_page, offset=pager['offset'])

        values.update({
            'open_tenders': open_tenders,
            'page_name': 'open_tender',
            'pager': pager,
            'default_url': '/my/open_tender',
            'open_tender_count': open_tender_count,
        })
        return request.render("sh_all_in_one_tender_bundle.open_portal_my_tenders", values)

    @http.route(['/my/open_tender/<int:open_tender_id>'], type='http', auth="user", website=True)
    def open_portal_my_tender_form(self, open_tender_id, report_type=None, access_token=None, message=False, download=False, **kw):
        open_tender = request.env['purchase.agreement'].sudo().browse(open_tender_id)
        try:
            if not request.env.user.has_group('sh_all_in_one_tender_bundle.sh_purchase_tender_user'):
                if open_tender.sh_open_tender:
                    if open_tender.sh_allow_portal_access:
                        if access_token:
                            if open_tender.sh_do_not_show_to_ids and request.env.user.partner_id.id in open_tender.sh_do_not_show_to_ids.ids:
                                return request.redirect('/my')
                            else:
                                open_tender_sudo = self._document_check_access('purchase.agreement', open_tender_id, access_token=access_token)
                        else:
                            if open_tender.sh_do_not_show_to_ids and request.env.user.partner_id.id in open_tender.sh_do_not_show_to_ids.ids:
                                return request.redirect('/my')
                            else:
                                open_tender_sudo = self._document_check_access('purchase.agreement', open_tender_id, access_token=None)
                    else:
                        if request.env.user.is_tendor_vendor:
                            if open_tender.sh_do_not_show_to_ids and request.env.user.partner_id.id in open_tender.sh_do_not_show_to_ids.ids:
                                return request.redirect('/my')
                            else:
                                open_tender_sudo = self._document_check_access('purchase.agreement', open_tender_id, access_token=None)
                        else:
                            return request.redirect('/my')
                else:
                    return request.redirect('/my')
        except (AccessError, MissingError):
            return request.redirect('/my')
        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=open_tender_sudo, report_type=report_type, report_ref='sh_all_in_one_tender_bundle.action_report_purchase_tender', download=download)
        if report_type == 'sh_po_tender_portal_xls':
            return self.sh_po_tender_portal_xls(open_tender)
        values = {
            'token': access_token,
            'open_tender': open_tender,
            'message': message,
            'bootstrap_formatting': True,
            'partner_id': open_tender.partner_id.id,
            'report_type': 'html',
        }
        return request.render('sh_all_in_one_tender_bundle.open_portal_tender_form_template', values)
    
    def sh_po_tender_portal_xls(self, tender):
        if tender:
            get_wizard_id = request.env[
                'purchase.agreement.xls.report'].sudo().create({
                    'parent_record':
                    tender.id,
                    'report_select':
                    'purchase_tender'
                })
            report_action = get_wizard_id.get_xls_reports()
            url = report_action.get('url')
            return request.redirect(url)


# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, api, _
from datetime import datetime
import datetime
from odoo.exceptions import UserError
import csv
import base64
import xlrd
from odoo.tools import ustr
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import pytz

class ImportTender(models.Model):
    _name = 'sh.import.tender'
    _description = 'Import Tender'

    @api.model
    def default_company(self):
        return self.env.company

    import_type = fields.Selection([('csv', 'CSV File'),
                                    ('excel', 'Excel File')],
                                   default="csv",
                                   string="Import File Type",
                                   required=True)
    file = fields.Binary(string="File", required=True)
    product_by = fields.Selection([('name', 'Name'),
                                   ('int_ref', 'Internal Reference'),
                                   ('barcode', 'Barcode')],
                                  default="name",
                                  string="Product By",
                                  required=True)
    sh_auto_create_rfq = fields.Boolean('Auto Create RFQ')
    sh_rfq_confirm = fields.Boolean('Auto Confirm Created RFQ')
    unit_price = fields.Selection([('sheet','Based on Sheet'),('cost','Based On Product Cost Price')],default='sheet',string='Unit Price',required=True)
    company_id = fields.Many2one(
        'res.company', 'Company', default=default_company, required=True)


    def show_success_msg(self, counter, confirm_rec, skipped_line_no):
        # open the new success message box
        view = self.env.ref('sh_message.sh_message_wizard')
        context = dict(self._context or {})
        dic_msg = str(counter) + " Records imported successfully \n"
        dic_msg = dic_msg + str(confirm_rec) + " RFQ created successfully"
        if skipped_line_no:
            dic_msg = dic_msg + "\nNote:"
        for k, v in skipped_line_no.items():
            dic_msg = dic_msg + "\nRow No " + k + " " + v + " "
        context['message'] = dic_msg

        return {
            'name': 'Success',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sh.message.wizard',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
        }

    def read_xls_book(self):
        book = xlrd.open_workbook(file_contents=base64.decodebytes(self.file))
        sheet = book.sheet_by_index(0)
        # emulate Sheet.get_rows for pre-0.9.4
        values_sheet = []
        for rowx, row in enumerate(map(sheet.row, range(sheet.nrows)), 1):
            values = []
            for colx, cell in enumerate(row, 1):
                if cell.ctype is xlrd.XL_CELL_NUMBER:
                    is_float = cell.value % 1 != 0.0
                    values.append(
                        str(cell.value) if is_float else str(int(cell.value)))
                elif cell.ctype is xlrd.XL_CELL_DATE:
                    is_datetime = cell.value % 1 != 0.0
                    # emulate xldate_as_datetime for pre-0.9.3
                    dt = datetime.datetime(*xlrd.xldate.xldate_as_tuple(
                        cell.value, book.datemode))
                    values.append(
                        dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT
                                    ) if is_datetime else dt.
                        strftime(DEFAULT_SERVER_DATE_FORMAT))
                elif cell.ctype is xlrd.XL_CELL_BOOLEAN:
                    values.append(u'True' if cell.value else u'False')
                elif cell.ctype is xlrd.XL_CELL_ERROR:
                    raise ValueError(
                        _("Invalid cell value at row %(row)s, column %(col)s: %(cell_value)s"
                          ) % {
                              'row':
                              rowx,
                              'col':
                              colx,
                              'cell_value':
                              xlrd.error_text_from_code.get(
                                  cell.value,
                                  _("unknown error code %s") % cell.value)
                        })
                else:
                    values.append(cell.value)
            values_sheet.append(values)
        return values_sheet

    def import_tender_apply(self):
        """Import Tender with some specific configuration"""
        tender_line_obj = self.env['purchase.agreement.line']
        tender_obj = self.env['purchase.agreement']
        if self:
            for rec in self:
                if self.import_type == 'csv' or self.import_type == 'excel':
                    # For CSV
                    counter = 1
                    skipped_line_no = {}
                    try:
                        values = []
                        if self.import_type == 'csv':
                            file = str(
                                base64.decodebytes(self.file).decode('utf-8'))
                            values = csv.reader(file.splitlines())

                        elif self.import_type == 'excel':
                            values = self.read_xls_book()
                        skip_header = True
                        running_tender = None
                        created_tender = False
                        created_tender_list_for_create_rfq = []
                        created_tender_list = []
                        for row in values:
                            try:
                                if skip_header:
                                    skip_header = False
                                    counter = counter + 1
                                    continue
                                if row[0] not in (None, ""):
                                    vals = {}

                                    if row[0] != running_tender:

                                        running_tender = row[0]
                                        tender_type = self.env['purchase.agreement.type'].sudo().search([('name','=',row[1])],limit=1)
                                        if tender_type:
                                            tender_vals = {
                                                'company_id': rec.company_id.id,'sh_agreement_type':tender_type.id}

                                            if row[2] not in (None,False,""):
                                                pr_id = self.env['res.users'].sudo().search([('name','=',row[2])],limit=1)
                                                if pr_id:
                                                    tender_vals.update({
                                                        'sh_purchase_user_id':pr_id.id,
                                                    })
                                                else:
                                                    skipped_line_no[str(
                                                        counter)] = " - Purchase Representative not found. "
                                                    counter = counter + 1
                                            if row[3] not in (None,False,""):
                                                vendor_ids = []
                                                if "," in row[3]:
                                                    vendors = row[3].split(",")
                                                    if vendors:
                                                        for vendor in vendors:
                                                            vendor_id = self.env['res.partner'].sudo().search([('name','=',vendor)],limit=1)
                                                            if vendor_id:
                                                                vendor_ids.append(vendor_id.id)
                                                else:
                                                    vendor_id = self.env['res.partner'].sudo().search([('name','=',row[3])],limit=1)
                                                    if vendor_id:
                                                        vendor_ids.append(vendor_id.id)
                                                if vendor_ids:
                                                    tender_vals.update({
                                                        'partner_ids':[(6,0,vendor_ids)],
                                                    })
                                                else:
                                                    skipped_line_no[str(
                                                        counter)] = " - Vendors not found. "
                                                    counter = counter + 1
                                            if row[7] not in (None,False,""):
                                                tender_vals.update({
                                                    'sh_source':row[7],
                                                })
                                            if row[4] not in (False,None,"") and isinstance(row[4], str):
                                                local = pytz.timezone(self.env.user.tz)
                                                naive = datetime.datetime.strptime(row[4], DEFAULT_SERVER_DATETIME_FORMAT)
                                                local_dt = local.localize(naive, is_dst=None)
                                                utc_dt = local_dt.astimezone(pytz.utc)
                                                tender_deadline = utc_dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                                                tender_vals.update({
                                                    'sh_agreement_deadline':tender_deadline
                                                })
                                            if row[5] not in (False,None,"") and isinstance(row[5], str):
                                                local = pytz.timezone(self.env.user.tz)
                                                naive = datetime.datetime.strptime(row[5], DEFAULT_SERVER_DATE_FORMAT)
                                                local_dt = local.localize(naive, is_dst=None)
                                                utc_dt = local_dt.astimezone(pytz.utc)
                                                sh_order_date = utc_dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                                                tender_vals.update({
                                                    'sh_order_date':sh_order_date
                                                })
                                            if row[6] not in (False,None,"") and isinstance(row[6], str):
                                                local = pytz.timezone(self.env.user.tz)
                                                naive = datetime.datetime.strptime(row[6], DEFAULT_SERVER_DATE_FORMAT)
                                                local_dt = local.localize(naive, is_dst=None)
                                                utc_dt = local_dt.astimezone(pytz.utc)
                                                sh_delivery_date = utc_dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                                                tender_vals.update({
                                                    'sh_delivery_date':sh_delivery_date
                                                })
                                            created_tender = tender_obj.create(tender_vals)
                                            if rec.sh_auto_create_rfq:
                                                created_tender.action_confirm()
                                            created_tender_list_for_create_rfq.append(created_tender.id)
                                            created_tender_list.append(created_tender.id)
                                        else:
                                            skipped_line_no[str(
                                                counter)] = " - Tender Type not found. "
                                            counter = counter + 1
                                            continue

                                    if created_tender:
                                        field_nm = 'name'
                                        if rec.product_by == 'name':
                                            field_nm = 'name'
                                        elif rec.product_by == 'int_ref':
                                            field_nm = 'default_code'
                                        elif rec.product_by == 'barcode':
                                            field_nm = 'barcode'

                                        search_product = self.env['product.product'].search(
                                            [(field_nm, '=', row[8])], limit=1)
                                        if search_product:
                                            vals.update(
                                                {'sh_product_id': search_product.id})
                                            if row[9] not in (False,None,""):
                                                vals.update(
                                                    {'sh_qty': float(row[9])})
                                            else:
                                                vals.update(
                                                    {'sh_qty': 1.00})
                                            if self.unit_price == 'sheet':
                                                if row[10] not in ['',None,False]:
                                                    vals.update({'sh_price_unit': float(row[10])})
                                                else:
                                                    vals.update({'sh_price_unit': 0.0})
                                            else:
                                                vals.update({'sh_price_unit': search_product.standard_price})
                                            vals.update(
                                                {'agreement_id': created_tender.id})
                                            line = tender_line_obj.create(vals)
                                            counter = counter + 1
                                        else:
                                            skipped_line_no[str(
                                                counter)] = " - Product not found. "
                                            counter = counter + 1
                                            if created_tender.id in created_tender_list_for_create_rfq:
                                                created_tender_list_for_create_rfq.remove(
                                                    created_tender.id)
                                            continue

                                    else:
                                        skipped_line_no[str(
                                            counter)] = " - Tender not created. "
                                        counter = counter + 1
                                        continue
                                else:
                                    skipped_line_no[str(
                                        counter)] = " - Tender Identifiction or Tender Type field is empty. "
                                    counter = counter + 1

                            except Exception as e:
                                skipped_line_no[str(
                                    counter)] = " - Value is not valid " + ustr(e)
                                counter = counter + 1
                                continue
                        created_rfq_list = []
                        if created_tender_list_for_create_rfq and rec.sh_auto_create_rfq:
                            tenders = tender_obj.search(
                                [('id', 'in', created_tender_list_for_create_rfq)])
                            if tenders:
                                for tender in tenders:
                                    if tender.partner_ids:
                                        for partner in tender.partner_ids:
                                            line_ids = []
                                            current_date = None
                                            if tender.sh_delivery_date:
                                                current_date = tender.sh_delivery_date
                                            else:
                                                current_date = fields.Datetime.now()
                                            if tender.sh_purchase_agreement_line_ids:
                                                for tender_line in tender.sh_purchase_agreement_line_ids:
                                                    line_vals = {
                                                        'product_id': tender_line.sh_product_id.id,
                                                        'name': tender_line.sh_product_id.name,
                                                        'date_planned': current_date,
                                                        'product_qty': tender_line.sh_qty,
                                                        'status': 'draft',
                                                        'agreement_id': tender.id,
                                                        'product_uom': tender_line.sh_product_id.uom_id.id,
                                                        'price_unit': tender_line.sh_price_unit,
                                                    }
                                                    line_ids.append((0, 0, line_vals))
                                            if line_ids:
                                                rfq_vals = {
                                                    'partner_id':partner.id,
                                                    'notes':tender.sh_notes,
                                                    'agreement_id':tender.id,
                                                    'user_id':tender.sh_purchase_user_id.id,
                                                }
                                                if rfq_vals:
                                                    rfq_id = self.env['purchase.order'].sudo().create(rfq_vals)
                                                    if rfq_id:
                                                        rfq_id.order_line = line_ids
                                                        if rec.sh_rfq_confirm:
                                                            rfq_id.button_confirm()
                                                        created_rfq_list.append(rfq_id.id)
                        else:
                            created_tender_list_for_create_rfq = []

                    except Exception as e:
                        raise UserError(
                            _("Sorry, Your csv file does not match with our format " + ustr(e)))

                    if counter > 1:
                        completed_records = len(created_tender_list)
                        confirm_rec = len(created_rfq_list)
                        res = self.show_success_msg(
                            completed_records, confirm_rec, skipped_line_no)
                        return res

# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, fields
import xlwt
from odoo.exceptions import UserError
import base64
import io


class PurchaseAgreementXlsReport(models.TransientModel):
    _name = 'purchase.agreement.xls.report'
    _description = 'Purchase Agreement Xls Report'

    parent_record = fields.Many2one('purchase.agreement')

    report_select = fields.Selection(
        [('purchase_tender', 'Purchase Tender'),
         ('analyze_quotation', 'Analyze Quotations')],
        string='Reports',
        default='purchase_tender')

    #XLS report button method to print xls report based on selection of report
    def get_xls_reports(self):
        parent_record = self.parent_record

        if self.report_select == 'purchase_tender':
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('Purchase Tender')
            bold_center = xlwt.easyxf(
                'font:height 280,bold True;align: vert center;align: horiz center;'
            )
            bold = xlwt.easyxf(
                'font:height 200,bold True;align: vert center;align: horiz center;pattern: pattern solid, fore_colour gray25;'
            )
            normal = xlwt.easyxf(
                'font:height 200;align: vert center;align: horiz center;')
            norma_bold = xlwt.easyxf(
                'font:height 200,bold True;align: vert center;')
            worksheet.row(1).height = 350
            if parent_record.state == 'draft':
                worksheet.write_merge(
                    1, 1, 0, 8, 'Purchase Tender' + " #" + parent_record.name,
                    bold_center)
            if parent_record.state == 'confirm':
                worksheet.write_merge(
                    1, 1, 0, 8, 'Purchase Tender' + " #" + parent_record.name,
                    bold_center)
            if parent_record.state == 'cancel':
                worksheet.write_merge(
                    1, 1, 0, 8,
                    'Cancelled Purchase Tender' + " #" + parent_record.name,
                    bold_center)
            if parent_record.state == 'bid_selection':
                worksheet.write_merge(
                    1, 1, 0, 8, 'Bid Selection Purchase Tender' + " #" +
                    parent_record.name, bold_center)
            if parent_record.state == 'closed':
                worksheet.write_merge(
                    1, 1, 0, 8,
                    'Closed Purchase Tender' + " #" + parent_record.name,
                    bold_center)
            worksheet.col(0).width = 10000
            worksheet.col(1).width = 8000
            worksheet.col(2).width = 8000
            worksheet.col(3).width = 8000
            worksheet.col(4).width = 8000
            worksheet.col(5).width = 8000
            worksheet.col(6).width = 8000
            worksheet.col(7).width = 8000
            worksheet.col(8).width = 8000
            worksheet.col(9).width = 8000

            worksheet.write_merge(3, 3, 0, 0, 'Tender Reference', norma_bold)
            if parent_record.sh_purchase_user_id:
                worksheet.col(2).width = 9000
                worksheet.write_merge(4, 4, 0, 0, 'Purchase Representative',
                                      norma_bold)
            worksheet.write_merge(5, 5, 0, 0, 'Purchase Tender Type',
                                  norma_bold)
            worksheet.write_merge(6, 6, 0, 0, 'Tender Deadline', norma_bold)
            worksheet.write_merge(7, 7, 0, 0, 'Source Document', norma_bold)
            worksheet.write_merge(8, 8, 0, 0, 'Project', norma_bold)

            ###############################################################################################

            worksheet.write_merge(3, 3, 1, 1, parent_record.name)
            if parent_record.sh_purchase_user_id:
                worksheet.col(2).width = 9000
                worksheet.write_merge(4, 4, 1, 1,
                                      parent_record.sh_purchase_user_id.name)

            worksheet.write_merge(5, 5, 1, 1,
                                  parent_record.sh_agreement_type.name)
            if parent_record.sh_agreement_deadline:
                worksheet.write_merge(6, 6, 1, 1,
                                      str(parent_record.sh_agreement_deadline))
            if parent_record.sh_source:
                worksheet.write_merge(7, 7, 1, 1, parent_record.sh_source)


            worksheet.write_merge(9, 9, 0, 0, 'Product', bold)
            worksheet.write_merge(9, 9, 1, 1, 'Product Ref', bold)
            worksheet.write_merge(9, 9, 2, 2, 'Quantity', bold)
            line_var = 11
            if parent_record.sh_purchase_agreement_line_ids:

                for line in parent_record.sh_purchase_agreement_line_ids:
                    worksheet.write_merge(
                        line_var, line_var, 0, 0,line.sh_product_id.name_get()[0][1])
                    worksheet.write_merge(
                        line_var, line_var, 1, 1,line.sh_product_id.default_code or '')
                    worksheet.write_merge(line_var, line_var, 2, 2,
                                        line.sh_qty or 0.0, normal)
                    line_var = line_var + 1

            if parent_record.sh_notes:
                worksheet.write_merge(line_var + 1, line_var + 1, 0, 0,
                                      parent_record.sh_notes)
            fp = io.BytesIO()
            workbook.save(fp)
            data = base64.encodebytes(fp.getvalue())
            IrAttachment = self.env['ir.attachment']
            attachment_vals = {
                "name": "Purchase Tender.xls",
                "res_model": "ir.ui.view",
                "type": "binary",
                "datas": data,
                "public": True,
            }
            fp.close()

            attachment = IrAttachment.search(
                [('name', '=', 'Purchase Tender'), ('type', '=', 'binary'),
                 ('res_model', '=', 'ir.ui.view')],
                limit=1)
            if attachment:
                attachment.write(attachment_vals)
            else:
                attachment = IrAttachment.create(attachment_vals)
            #TODO: make user error here
            if not attachment:
                raise UserError('There is no attachments...')

            url = "/web/content/" + str(attachment.id) + "?download=true"
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }

        if self.report_select == 'analyze_quotation':
            workbook = xlwt.Workbook()
            worksheet = workbook.add_sheet('Analyze Quotations')
            bold_center = xlwt.easyxf(
                'font:height 280,bold True;align: vert center;align: horiz center;'
            )
            bold = xlwt.easyxf(
                'font:height 200,bold True;align: vert center;align: horiz center;pattern: pattern solid, fore_colour gray25;'
            )
            green_font = xlwt.easyxf(
                'font:height 210,color green;align: vert center;')
            green_font_bold = xlwt.easyxf(
                'font:height 230,color green,bold True;align: vert center;')
            black_font_bold = xlwt.easyxf(
                'font:height 230,color black,bold True;align: vert center;')
            normal = xlwt.easyxf(
                'font:height 200;align: vert center;align: horiz center;')
            worksheet.row(1).height = 350
            worksheet.write_merge(1, 1, 0, 5, 'Analyze Quotations',
                                  bold_center)

            domain = [("state", "in", ['draft']),
                      ('agreement_id', '=', parent_record.id)]
            get_purchase_order = self.env['purchase.order'].search(domain)
            product_price_dic = {}
            if get_purchase_order:
                domain = [('order_id', 'in', get_purchase_order.ids)]
                for line in self.env['purchase.order.line'].search(domain):
                    price_list = product_price_dic.get(line.product_id.id, [])
                    price_list.append(line.price_unit)
                    product_price_dic.update({line.product_id.id: price_list})
                for k, v in product_price_dic.items():
                    lowest_price = min(v)
                    product_price_dic.update({k: lowest_price})

            low_amount_list = []
            if get_purchase_order:
                for rec in get_purchase_order:
                    low_amount_list.append(rec.amount_untaxed)
            low_amount_list.sort()
            if get_purchase_order:
                partner_var = 3
                for rec in get_purchase_order:
                    heading_var = partner_var + 3
                    worksheet.write_merge(
                        partner_var, partner_var, 0, 0, rec.partner_id.name,
                        xlwt.easyxf('font:height 200,bold True;'))
                    worksheet.write_merge(
                        partner_var + 1, partner_var + 1, 1, 1, rec.name,
                        xlwt.easyxf(
                            'font:height 200,bold True;align: vert center;align: horiz center;'
                        ))
                    worksheet.col(0).width = 8000
                    worksheet.col(1).width = 8000
                    worksheet.write_merge(heading_var, heading_var, 0, 0,
                                          'Description', bold)
                    worksheet.write_merge(heading_var, heading_var, 1, 1,
                                          'Product', bold)
                    worksheet.write_merge(heading_var, heading_var, 2, 2,
                                          'Product Ref', bold)
                    worksheet.write_merge(heading_var, heading_var, 3, 3,
                                          'Price', bold)
                    worksheet.write_merge(heading_var, heading_var, 4, 4,
                                          'Quantity', bold)
                    worksheet.write_merge(heading_var, heading_var, 5, 5,
                                          'Amount', bold)
                    line_var = heading_var + 1
                    total_var = 0
                    for line in rec.order_line:
                        if not line.display_type:
                            if product_price_dic.get(
                                    line.product_id.id) == line.price_unit:
                                worksheet.write_merge(line_var, line_var, 0, 0,
                                                    line.name,
                                                    green_font)
                                worksheet.write_merge(line_var, line_var, 1, 1,
                                                    line.product_id.name_get()[0][1],
                                                    green_font)
                                worksheet.write_merge(line_var, line_var, 2, 2,
                                                    line.product_id.default_code or '',
                                                    green_font)
                                worksheet.write_merge(line_var, line_var, 3, 3,
                                                    line.price_unit, green_font)
                                worksheet.write_merge(line_var, line_var, 4, 4,
                                                    line.product_qty, green_font)
                                worksheet.write_merge(line_var, line_var, 5, 5,
                                                    line.price_subtotal,
                                                    green_font)
                                total_var = total_var + line.price_subtotal
                                line_var = line_var + 1
                        if line.display_type == 'line_section':
                            worksheet.write_merge(line_var, line_var, 0, 5,
                                                line.name or '', bold)
                        if line.display_type == 'line_note':
                            worksheet.write_merge(line_var, line_var, 0, 5,
                                                line.name or '', bold)
                    if low_amount_list[0] == total_var:
                        worksheet.write_merge(line_var, line_var, 5, 5,
                                              total_var, green_font_bold)
                    else:
                        worksheet.write_merge(line_var, line_var, 5, 5,
                                              total_var, black_font_bold)
                    partner_var = partner_var + 10

            fp = io.BytesIO()
            workbook.save(fp)

            data = base64.encodebytes(fp.getvalue())
            IrAttachment = self.env['ir.attachment']
            attachment_vals = {
                "name": "Analyze Quotations.xls",
                "res_model": "ir.ui.view",
                "type": "binary",
                "datas": data,
                "public": True,
            }
            fp.close()
            attachment = IrAttachment.search(
                [('name', '=', 'Analyze Quotations'), ('type', '=', 'binary'),
                 ('res_model', '=', 'ir.ui.view')],
                limit=1)
            if attachment:
                attachment.write(attachment_vals)
            else:
                attachment = IrAttachment.create(attachment_vals)
            #TODO: make user error here
            if not attachment:
                raise UserError('There is no attachments...')

            url = "/web/content/" + str(attachment.id) + "?download=true"
            return {
                'type': 'ir.actions.act_url',
                'url': url,
                'target': 'new',
            }

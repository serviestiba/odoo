# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "All In One Tender Management | Purchase Tender Bundle | Tender Full Flow Management",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "license": "OPL-1",
    "category": "Purchases",
    "summary": "Manage Multiple Tenders Request For Quotation Manage Same Partner Tender Management Purchase Tender Management PO Tender Management Bid Apply Analyze Tender Analyze RFQ Best Supplier At Best Price Tender Send To Multiple Vendor Change RFQ Price Odoo Multi Vendor Purchase Tender Vendor Tender Portal Purchase Order Tender Management PO Tender Multiple Purchase Tender Purchase Agreement Purchase Bidding Multi Vendor Bidding Manage Purchase Bid Process Vendor BID Purchase Order Bid Manage Tender RFQ Bid Odoo Tender Management System Odoo Tender Management App Tender Management Software Odoo Tender Vendor Purchase Tender Vendor Tender Portal Supplier Multiple Purchase Tender",
    "description": """Nowadays in a competitive market, several vendors sell the same products and everyone has their price so it will difficult to manage multiple tenders list at a time even in odoo there is no kind of feature where you can manage multiple tenders & RFQ's in a single list. Here the vendor can change the price from portal or website for tenders & RFQ's. You can see tender portal details from RFQ. This module helps in the online signature in the RFQ at the portal. You can print "Purchase Tender" & "Analyze Quotations" PDF report.""",
    "version": "16.0.6",
    "depends": [
        "purchase",
        "stock",
        "account",
        "mail",
        "portal",
        "utm",
        "website",
        "sh_message",
        "sh_backend_base",
    ],
    "application": True,
    "data": [
        'sh_po_tender_management/security/sh_purchase_tender_security.xml',
        'sh_po_tender_management/security/ir.model.access.csv',
        'sh_po_tender_management/data/sh_purchase_agreement_data.xml',
        'sh_po_tender_management/views/res_config_seetings.xml',
        'sh_po_tender_management/views/sh_purchase_agreement_type_view.xml',
        'sh_po_tender_management/views/res_users.xml',
        'sh_po_tender_management/views/sh_purchase_agreement_view.xml',
        'sh_po_tender_management/views/sh_bidline_view.xml',
        'sh_po_tender_management/views/sh_report_purchase_tender_template.xml',
        'sh_po_tender_management/views/report_analyze_quotations.xml',
        'sh_po_tender_management/views/report_views.xml',
        'sh_po_tender_management/data/sh_purchase_tender_email_data.xml',
        'sh_po_tender_management/wizard/sh_update_qty_wizard_view.xml',
        'sh_po_tender_management/wizard/sh_purchase_order_wizard_view.xml',
        'sh_po_tender_management/wizard/tender_xls_wizard.xml',
        'sh_po_tender_management/wizard/create_multi_rfq_wizard.xml',
        'sh_po_tender_management/wizard/import_tender_line.xml',
        'sh_po_tender_management/wizard/sh_import_tender_views.xml',
        
        'sh_rfq_portal/security/ir.model.access.csv',
        'sh_rfq_portal/views/purchase.xml',
        'sh_rfq_portal/views/portal_templates.xml',
        'sh_rfq_portal/data/cron_deactivate_portal_access.xml',
        
        'sh_po_tender_portal/security/ir.model.access.csv',
        'sh_po_tender_portal/views/res_config_setting.xml',
        'sh_po_tender_portal/views/attachment.xml',
        'sh_po_tender_portal/views/tender_portal_template_view.xml',
        'sh_po_tender_portal/views/open_tender_portal_template.xml',
        'sh_po_tender_portal/views/tender_rfq_portal_view.xml',
        'sh_po_tender_portal/data/cron_garbase_collection.xml',

        "sh_vendor_signup/views/assets_frontend.xml",
        "sh_vendor_signup/views/vendor_sign_up_template.xml",
        "sh_vendor_signup/views/res_partner_view_inherit.xml",
        "sh_vendor_signup/views/res_config_settings.xml",
        "sh_vendor_signup/data/vendor_sign_up_menu.xml",
        "sh_vendor_signup/data/mail_template.xml",

        'sh_rfq_portal_signature/views/purchase_view.xml',
        'sh_rfq_portal_signature/views/portal_templates.xml',
    ],
    "images": ["static/description/background.gif", ],
    "auto_install": False,
    "installable": True,
    "price": 350,
    "currency": "EUR"
}

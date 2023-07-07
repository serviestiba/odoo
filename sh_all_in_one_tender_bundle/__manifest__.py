# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "All In One Tender Management | Purchase Tender Bundle | Tender Full Flow Management",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "license": "OPL-1",
    "category": "Purchases",
    "summary": "Manage Multiple Tenders Request For Quotation Manage Same Partner Tender Management Purchase Tender Management PO Tender Management Bid Apply Analyze Tender Analyze RFQ Best Supplier At Best Price Tender Send To Multiple Vendor Change RFQ Price Apps for purchase Material Requisitions Request  purchase product Requisitions Request Material Requisition for tender Material Requisition for manufacturing order Product Request on RFQ Product Request on Tender Product Request on manufacturing order Odoo",
    "description": """Nowadays in a competitive market, several vendors sell the same products and everyone has their price so it will difficult to manage multiple tenders list at a time even in odoo there is no kind of feature where you can manage multiple tenders & RFQ's in a single list. Here the vendor can change the price from portal or website for tenders & RFQ's. You can see tender portal details from RFQ. This module helps in the online signature in the RFQ at the portal. You can print "Purchase Tender" & "Analyze Quotations" PDF report.""",
    "version": "16.0.2",
    "depends": [
        "purchase",
        "stock",
        "account",
        "mail",
        "portal",
        "utm",
        "website",
        "sh_message",
    ],
    "application": True,
    "data": [
        'sh_po_tender_management/security/purchase_agreement_security.xml',
        'sh_po_tender_management/security/ir.model.access.csv',
        'sh_po_tender_management/data/purchase_agreement_data.xml',
        'sh_po_tender_management/views/res_config_setting_views.xml',
        'sh_po_tender_management/views/purchase_agreement_type_views.xml',
        'sh_po_tender_management/views/res_users_views.xml',
        'sh_po_tender_management/views/purchase_agreement_views.xml',
        'sh_po_tender_management/views/purchase_order_views.xml',
        'sh_po_tender_management/report/purchase_agreement_templates.xml',
        'sh_po_tender_management/report/report_analyze_quotations_report_templates.xml',
        'sh_po_tender_management/report/purchase_agreement_report_views.xml',
        'sh_po_tender_management/data/mail_template_data.xml',
        'sh_po_tender_management/wizard/update_qty_wizard_views.xml',
        'sh_po_tender_management/wizard/purchase_order_wizard_views.xml',
        'sh_po_tender_management/wizard/purchase_agreement_xls_report_wizard_views.xml',
        'sh_po_tender_management/wizard/sh_import_tender_lines_wizard_views.xml',
        'sh_po_tender_management/wizard/sh_create_multi_rfq_wizard_views.xml',

        'sh_rfq_portal/security/ir.model.access.csv',
        'sh_rfq_portal/data/ir_cron_data.xml',
        'sh_rfq_portal/views/purchase_order_views.xml',
        'sh_rfq_portal/views/purchase_order_templates.xml',

        'sh_po_tender_portal/security/ir.model.access.csv',
        'sh_po_tender_portal/views/res_config_setting.xml',
        'sh_po_tender_portal/views/purchase_agreement_views.xml',
        'sh_po_tender_portal/views/ir_attachment_views.xml',
        'sh_po_tender_portal/views/purchase_agreement_templates.xml',
        'sh_po_tender_portal/views/purchase_order_templates.xml',
        'sh_po_tender_portal/data/ir_cron_data.xml',

        "sh_vendor_signup/views/vendor_sign_up_templates.xml",
        "sh_vendor_signup/views/res_partner_views.xml",
        "sh_vendor_signup/views/res_config_settings_views.xml",
        "sh_vendor_signup/data/vendor_sign_up_menu.xml",
        "sh_vendor_signup/data/mail_template_data.xml",

        'sh_rfq_portal_signature/views/purchase_order_views.xml',
        'sh_rfq_portal_signature/views/purchase_order_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'sh_all_in_one_tender_bundle/sh_po_tender_portal/static/src/js/purchase_agreement.js',
            'sh_all_in_one_tender_bundle/sh_rfq_portal/static/src/js/portal.js',
            'sh_all_in_one_tender_bundle/sh_vendor_signup/static/src/scss/style.scss',
            'sh_all_in_one_tender_bundle/sh_vendor_signup/static/src/js/country_state.js',
            'sh_all_in_one_tender_bundle/sh_vendor_signup/static/src/js/sh_vendor_signup.js',
            'sh_all_in_one_tender_bundle/sh_vendor_signup/static/src/js/lib/bootstrap-multiselect.js',
        ]
    },
    "images": ["static/description/background.gif", ],
    "auto_install": False,
    "installable": True,
    "price": 350,
    "currency": "EUR"
}

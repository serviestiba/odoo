# -*- coding: utf-8 -*-
##############################################################################
#                 @author IDCA
##############################################################################

{
    'name': 'Serviestiba Odoo',
    'version': '1.3',
    'description': ''' Changes for Serviestiba
    ''',
    'category': 'Purchase',
    'author': 'IDCA',
    'website': '',
    'depends': [
        'purchase','maintenance'
    ],
    'data': [
        'data/maintenance_sequence_data.xml',
        'views/purchase_order_view.xml',
        'views/stock_picking_view.xml',
        'views/maintenance_request_view.xml',
    ],
    'images': [],
    'application': False,
    'installable': True,
    'price': 0.00,
    'currency': 'USD',
    'license': 'OPL-1',
}

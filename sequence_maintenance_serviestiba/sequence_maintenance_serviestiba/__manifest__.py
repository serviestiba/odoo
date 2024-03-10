# -*- coding: utf-8 -*-
##############################################################################
#                 @author IDCA
##############################################################################

{
    'name': 'Sequence Maintenance',
    'version': '16.1',
    'description': ''' Changes for sequence in maintenance
    ''',
    'category': 'Purchase',
    'author': 'IDCA',
    'website': '',
    'depends': [
        'maintenance'
    ],
    'data': [
        'data/maintenance_sequence_data.xml',
        'views/maintenance_request_view.xml',
    ],
    'images': [],
    'application': False,
    'installable': True,
    'price': 0.00,
    'currency': 'USD',
    'license': 'OPL-1',
}

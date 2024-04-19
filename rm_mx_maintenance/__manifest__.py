# -*- coding: utf-8 -*-
{
    'name': 'Rm_mx_maintenance',
    'version': '',
    'description': """ Rm_mx_maintenance Description """,
    'summary': """ Rm_mx_maintenance Summary """,
    'author': '',
    'website': '',
    'category': '',
    'depends': ['base', 'maintenance', 'stock'],
    "data": [
        'security/ir.model.access.csv',
        "views/maintenance_request_views.xml",
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

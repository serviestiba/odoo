# -*- encoding: utf-8 -*-
{
    'name': 'Invisible Maintenance Stage',
    'version': '15.1.0',
    'author': 'IDCA',
    'summary': 'Maintenance stage by group',
    'website': '',
    'category': 'Base',
    'description': """
    """,
    'depends': ['maintenance'],
    'data': [
        'security/groups.xml',
        'security/ir_rules.xml',
        'views/maintenance_stage_views.xml',
    ],
    'images': [],
    'qweb': [],
    'installable': True,
    'application': False,
    'license': 'OPL-1',
}

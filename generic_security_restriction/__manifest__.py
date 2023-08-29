{
    "name": "Generic Security Restriction",
    "version": "16.0.0.22.0",
    "author": "Center of Research and Development",
    "website": "https://crnd.pro",
    "license": 'OPL-1',
    "summary": """
        Hide Menu / Specific Menus / Restrict Menu / Restrict Actions
        Hide Field On The View / Make Field Readonly / Model Restrictions
        Hide Stat Button / Change Parameters of M2o Fields:
        ('no_open', 'no_create', 'no_quick_create', 'no_create_edit')
    """,
    'category': 'Technical Settings',
    'depends': [
        'base',
        'web',
    ],
    'data': [
        'security/ir.model.access.csv',

        'data/user_admin.xml',

        'views/ir_ui_menu_view.xml',
        'views/res_groups_view.xml',
        'views/res_users_view.xml',
        'views/ir_model_view.xml',
        'views/ir_actions.xml',
        'views/generic_security_model_restriction.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'price': 21.0,
    'currency': 'EUR',
}

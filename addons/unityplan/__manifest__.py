# -*- coding: utf-8 -*-
{
    'name': "Unityplan",

    'summary': """
        The main module for running a Unityplan website""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Unityplan",
    'website': "https://www.unityplan.one",
    'license': 'LGPL-3',
    'category': 'Website',
    'version': '0.1',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'base_user_role'],

    # always loaded
    'data': [

        'data/res_country_data.xml',
        'data/res_currency_data.xml',
        'data/res.country.state.csv',
        'data/initialize_groups_roles.xml',

        'security/groups_roles.xml',
        'security/ir.model.access.csv',

        'views/unityplan_category_tags_views.xml',
        'views/unityplan_dashboard_views.xml',
        'views/unityplan_menus.xml',

        'views/base/res_config_settings_views.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}

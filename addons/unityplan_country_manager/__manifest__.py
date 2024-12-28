# -*- coding: utf-8 -*-
{
    'name': "Unityplan - Country Manager",

    'summary': """
        The Unityplan Country Manager module allows users defined as Country Managers to manage users from the same 
        country as the country manager.""",

    'description': """
        The Unityplan Country Manager module allows users defined as Country Managers to manage users from the same
        country as the country manager. The module adds a new menu item to the website profile menu called "Country
        Manager" which allows the country manager to manage users from the same country as the country manager. The
        module also adds a new menu item to the website profile menu called "Country Manager" which allows the country
        manager to manage users from the same country as the country manager. The module also adds a new menu item to
        the website profile menu called "Country Manager" which allows the country manager to manage users from the same
        country as the country manager. The module also adds a new menu item to the website profile menu called "Country
        Manager" which allows the country manager to manage users from the same country as the country manager.
    """,

    'author': "Unityplan",
    'website': "https://www.unityplan.one",
    'license': 'LGPL-3',
    'category': 'Website',
    'version': '0.2',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['unityplan', 'unityplan_website'],
    'assets': {
        'web.assets_frontend': [
            'unityplan_country_manager/static/src/js/frontend/manage.js',
            'unityplan_country_manager/static/src/scss/country_manager.scss',
        ],
    },
    'data': [
        'security/groups_roles.xml',
        'security/ir.model.access.csv',
        'security/record_rules.xml',
        'views/backend/unityplan_territories_views.xml',
        'views/backend/unityplan_menus.xml',
        'views/frontend/manage.xml',
        'views/frontend/error_pages.xml',
    ],
    #'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
}

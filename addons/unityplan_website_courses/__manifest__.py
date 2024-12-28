# -*- coding: utf-8 -*-
{
    'name': "Unity Plan - Courses",

    'summary': """
        The Unity Plan e-learning platform""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Unity Plan",
    'website': "https://www.unityplan.one",
    'license': 'LGPL-3',
    'category': 'Website',
    'version': '0.2',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['unityplan', 'unityplan_website_forum', 'website_slides', 'website_slides_survey'],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/unityplan_menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
}

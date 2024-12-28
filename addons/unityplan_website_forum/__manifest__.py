# -*- coding: utf-8 -*-
{
    'name': "Unity Plan - Forum",

    'summary': """
        The Unity Plan Forum""",

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
    'depends': ['unityplan', 'website_forum'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/unityplan_forum_views.xml',
        'views/unityplan_menus.xml',
        'views/unityplan_website_forum.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo/demo.xml',
    ],
    'installable': True,
    'application': False,
    'assets': {
        # 'website.assets_editor': [
        #     'unityplan_website_forum/static/src/js/systray_items/*.js',
        # ],
        # 'web.assets_tests': [
        #     'unityplan_website_forum/static/tests/**/*',
        # ],
        # 'web.assets_common': [
        #     'unityplan_website_forum/static/src/js/tours/unityplan_website_forum.js',
        # ],
        # 'web.assets_frontend': [
        #     'unityplan_website_forum/static/src/js/tours/unityplan_website_forum.js',
        #     'unityplan_website_forum/static/src/scss/unityplan_website_forum.scss',
        #     'unityplan_website_forum/static/src/js/unityplan_website_forum.js',
        #     'unityplan_website_forum/static/src/js/unityplan_website_forum.share.js',
        #     'unityplan_website_forum/static/src/xml/unityplan_public_templates.xml',
        # ],
        # 'web_editor.assets_wysiwyg': {
        #     'unityplan_website_forum/static/src/xml/unityplan_forum_wysiwyg.xml',
        # },
    },
    'license': 'LGPL-3',
}

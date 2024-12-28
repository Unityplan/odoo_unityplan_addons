# -*- coding: utf-8 -*-
{
    'name': "Unityplan - Website",

    'summary': """
        The Unityplan website""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Unityplan",
    'website': "https://www.unityplan.one",
    'license': 'LGPL-3',
    'category': 'Website',
    'version': '0.2',
    'sequence': 1,

    # any module necessary for this one to work correctly
    'depends': ['unityplan', 'website', 'website_blog', 'website_profile'],
    'assets': {
        'web.assets_frontend': [
            'unityplan_website/static/lib/jquery-ui/jquery-ui.min.js',
            'unityplan_website/static/lib/jquery-ui/jquery-ui.min.css',
            'unityplan_website/static/lib/jquery-ui/jquery-ui.theme.min.css',
            'unityplan_website/static/lib/jquery-ui/jquery-ui.structure.min.css',
            'unityplan_website/static/src/js/website_profile/profile_shared.js',
            'unityplan_website/static/src/js/website_profile/profile_edit.js',
            'unityplan_website/static/src/js/code_of_conduct/invisible_elements.js',
            'unityplan_website/static/src/scss/website_profile/website_profile.scss',

        ],
        'web.assets_backend': [
            'unityplan_website/static/src/scss/web/fields.scss',
        ],
    },
    # always loaded
    'data': [
        'views/portal/overrides.xml',
        'views/website_profile/overrides.xml',
        'views/website_profile/profile_shared_views.xml',
        'views/website_profile/profile_edit.xml',
        'views/website_profile/profile_settings.xml',
        'views/website_profile/profile_delete_account.xml',
        'views/website_profile/profile_blocked_account.xml',
        'views/website_profile/profile_revoke_sessions.xml',
        'views/website_profile/profile_change_password.xml',
        'views/website_profile/profile_change_totp.xml',
        'views/website_profile/profile_view_personal.xml',
        'views/website_profile/profile_view_public.xml',
        'views/pages/code_of_conduct.xml',
        'views/snippets/s_text_block_code_of_conduct_page_header.xml',
        'views/snippets/s_text_block_code_of_conduct_welcome.xml',
        'views/snippets/s_text_block_code_of_conduct_course_message.xml',
    ],
    'installable': True,
    'application': False,
}

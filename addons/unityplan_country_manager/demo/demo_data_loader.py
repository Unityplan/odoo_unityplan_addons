# File: dev-addons/unityplan_country_manager/data/demo_data_loader.py



def load_demo_data(env, registry):
    config = env['res.config.settings'].create({})
    if not config.demo_data_loaded:
        users_data = [
            {
                'name': 'Portal Demo User 1',
                'login': 'new_portal_user_1@techzone.dk',
                'email': 'new_portal_user_1@techzone.dk',
                'groups_id': [(4, env.ref('base.group_portal').id)],
                'country_id': env.ref('base.dk').id,
                'password': 'password',
            },
            # Add other users here
        ]
        for user_data in users_data:
            if not env['res.users'].search([('login', '=', user_data['login'])]):
                env['res.users'].create(user_data)
        config.demo_data_loaded = True
        config.save()
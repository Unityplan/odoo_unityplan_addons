from odoo import http, _
from odoo.http import request
from odoo.exceptions import UserError

class WebsiteCountryManager(http.Controller):

    @http.route('/cm/manage', type='http', auth='user', website=True)
    def manage_users(self, **kwargs):
        user = request.env.user
        country_manager = request.env['res.country_manager'].search([('related_user_id', '=', user.id)], limit=1)
        if not country_manager:
            return request.render(
                'unityplan_country_manager.error_403_forbidden_page')  # Render a 403 Forbidden page if not a country manager

        return request.render('unityplan_country_manager.country_manager_manage_users_page', {
        })

    @http.route('/cm/manage/users', type='json', auth='user')
    def get_users(self):
        user = request.env.user
        country_manager = request.env['res.country_manager'].search([('related_user_id', '=', user.id)], limit=1)
        if not country_manager:
            return {'error': 'Not authorized'}

        # Fetch users managed by the country manager
        # Exclude the current user and internal users
        # Exclude users from countries not managed by the country manager
        #
        # To include both active and inactive users in the search, you need to remove the default filter that only
        # includes active users. You can achieve this by adding the active_test=False context to the search.
        users = request.env['res.users'].with_context(active_test=False).search([
            ('partner_id.country_id', 'in', country_manager.country_ids.ids),
            ('id', '!=', user.id),  # Exclude the current user
            ('share', '=', True)  # Exclude internal users
        ])

        # Fetch timezones and languages
        timezones = {country.id: country.get_timezones_by_country() for country in country_manager.country_ids}
        languages = request.env['res.lang'].search([]).read(['code', 'name'])

        return {
            'user_id': user.id,
            'is_country_manager': country_manager.is_country_manager,
            'is_community_manager': country_manager.is_community_manager,
            'country_manager_managed_countries': [{'id': country.id, 'name': country.name} for country in
                                                  country_manager.country_ids],
            'users': [
                {
                    'id': u.id,
                    'login': u.login or '',
                    'name': u.name or '',
                    'email': u.email or '',
                    'active': u.active,
                    'create_date': u.create_date,
                    'login_date': bool(u.login_date),
                    'lang': u.lang or '',
                    'lang_name': dict(request.env['res.lang'].get_installed()).get(u.lang, u.lang),
                    'tz': u.tz or '',
                    'zip': u.zip or '',
                    'city': u.city or '',
                    'country': u.country_id.name or '',
                    'phone': u.phone or '',
                    'comment': u.comment or '',
                    'is_published': u.is_published,
                    'email_verified': bool(u.email_normalized) if u.email_normalized else False
                } for u in users
            ],
            'timezones': timezones,
            'languages': languages
        }

    @http.route('/cm/manage/users/edit', type='json', auth='user')
    def edit_user(self, user_id, name=None, email=None, phone=None, zip=None, city=None, country=None, tz=None,
                  lang=None, comment=None, send_invitation_email=None, send_reset_password_email=None,
                  request_code_of_conduct=None, block_user=None):
        messages = []
        user = request.env.user

        country_manager = request.env['res.country_manager'].search([('related_user_id', '=', user.id)], limit=1)

        if not country_manager:
            return {'error': 'Not authorized'}

        user_to_edit = request.env['res.users'].browse(user_id)
        if not user_to_edit:
            return {'error': 'User not found'}

        if user_to_edit.partner_id.country_id.id not in country_manager.country_ids.ids:
            return {'error': 'Not authorized to edit this user'}

        country_id = request.env['res.country'].search([('name', '=', country)], limit=1)
        if not country_id:
            return {'error': 'Invalid country'}

        user_to_edit.write({
            'name': name,
            'email': email,
            'phone': phone,
            'zip': zip,
            'city': city,
            'country_id': country_id.id,
            'tz': tz,
            'lang': lang,
            'comment': comment,
        })
        messages.append('User details updated successfully')

        # Send invitation email
        if send_invitation_email:
            template = request.env.ref('auth_signup.mail_template_user_signup_account_created')
            if not template:
                return {'error': 'Signup: No email template found for sending invitation email.'}
            if not user_to_edit.email:
                template.sudo().send_mail(user_id, email_values={'email_to': user_to_edit.login}, force_send=True)
            else:
                template.sudo().send_mail(user_to_edit.id, force_send=True)
            messages.append('Invitation email sent successfully.')

        if request_code_of_conduct:
            group_code_of_conduct_not_completed = request.env.ref('unityplan.group_code_of_conduct_not_completed')
            if group_code_of_conduct_not_completed:
                user_to_edit.sudo().write({'groups_id': [(4, group_code_of_conduct_not_completed.id)]})
            messages.append('Code of conduct requested successfully.')

        if block_user:
            user_to_edit.active = False
            messages.append('User blocked successfully.')
        else:
            user_to_edit.active = True

        if send_reset_password_email:
            try:
                user_to_edit.sudo().action_reset_password()
                messages.append('Reset password email sent successfully.')
            except Exception as e:
                return {'error': f'Failed to send reset password email: {str(e)}'}

        if not user_to_edit:
            return {'error': 'Failed to update user'}

        return {
            'title': 'Updated',
            'message': ', '.join(messages)
        }

    @http.route('/cm/manage/users/create', type='json', auth='user')
    def create_user(self, name, email, country):
        user = request.env.user
        country_id = int(country)
        country_manager = request.env['res.country_manager'].search([('related_user_id', '=', user.id)], limit=1)
        if not country_manager:
            return {'error': 'Not authorized'}

        # Check if the email is already used
        existing_user = request.env['res.users'].search([('login', '=', email)], limit=1)
        if existing_user:
            return {'error': 'There is already an user account with this e-mail address'}

        # Check that user is allowed to create a user in the selected country
        if country_id not in country_manager.country_ids.ids:
            return {'error': 'Not authorized to create user in this country'}
        ## Convert country to integer and get the country record
        try:
            country_record = request.env['res.country'].browse(country_id)
        except ValueError:
            return {'error': 'Invalid country ID'}

        if not country_record.exists():
            return {'error': 'Invalid country'}

        # Create the new user
        new_user = request.env['res.users'].sudo().create({
            'name': name,
            ##'email': email,
            'login': email,
            'active': True,
            'share': True,  # Ensure the user is a portal user
            'country_id': country_record.id,
        })

        # Ensure the 'share' field is set to True
        new_user.sudo().write({'share': True})

        if not new_user:
            return {'error': 'Failed to create user'}

        # Send invitation email
        template = request.env.ref('auth_signup.mail_template_user_signup_account_created')
        if not template:
            return {'error': 'Signup: No email template found for sending invitation email.'}
        template.sudo().send_mail(new_user.id, email_values={'email_to': email}, force_send=True)

        return {
            'title': 'User created successfully',
            'message': 'Invitation email is send to the user'
        }

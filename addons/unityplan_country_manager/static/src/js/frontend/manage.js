/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.CountryManager_ManageUsers = publicWidget.Widget.extend({
    selector: '#country_manager_manage_users_app',
    events: {
        'click .user_row': '_onEditUserClick',
        'click #saveUserChanges': '_onSaveUserChanges',
        'input #search_field': '_onSearchInput',
        'change #editUserCountry': '_onCountryChange',
        'click #createUser': '_onCreateUserClick',
        'click #createUserButton': '_onCreateUserChanges',
    },

    init() {
        this._super(...arguments);
        this.rpc = this.bindService("rpc");
        this.orm = this.bindService("orm");
        this.notification = this.bindService("notification");
        this.users = [];
        this.countries = [];
        this.timezones = [];
        this.languages = [];
        this.filteredUsers = [];
        this.currentPage = 1;
        this.usersPerPage = 10;
    },

    start: async function () {
        await this._super.apply(this, arguments);
        await this._getUsers();
        this._initializeTooltips();

        // Add event listener to checkboxes to allow only one to be checked at a time
        $('.form-check-input').on('change', function () {
            if ($(this).is(':checked')) {
                $('.form-check-input').not(this).prop('checked', false);
            }
        });

        // Add event listeners for the new filter checkboxes
        $('#filterEmailNotVerified').on('change', this._filterUsers.bind(this));
        $('#filterNeverConnected').on('change', this._filterUsers.bind(this));
        $('#filterAccountInactive').on('change', this._filterUsers.bind(this));

        // Populate country dropdown
        this._populateCountryDropdown();

        // Add event listener for country dropdown
        $('#countryFilter').on('change', this._filterUsers.bind(this));

        // Initialize WYSIWYG editor for the textarea when the modal is shown
        // $('#editUserModal').on('shown.bs.modal', function () {
        //     const userCommentId = $('#editUserModal').data('user-comment-id');
        //     if (!userCommentId) {
        //         console.error('User comment ID is not set.');
        //         return;
        //     }
        //     const textareaId = `content-${userCommentId}`;
        //     const textarea = document.getElementById(textareaId);
        //     if (textarea) {
        //         const options = {
        //             toolbarTemplate: 'website_forum.web_editor_toolbar',
        //             toolbarOptions: {
        //                 showColors: false,
        //                 showFontSize: false,
        //                 showHistory: true,
        //                 showHeading1: false,
        //                 showHeading2: false,
        //                 showHeading3: false,
        //                 showLink: true,
        //                 showImageEdit: true,
        //             },
        //             resizable: true,
        //             userGeneratedContent: true,
        //             height: 200,
        //         };
        //         loadWysiwygFromTextarea(this, textarea, options).then(wysiwyg => {
        //             $('#editUserModal').find('.note-editable').find('img.float-start').removeClass('float-start');
        //         }).catch(error => {
        //             console.error('Error initializing WYSIWYG editor:', error);
        //         });
        //     } else {
        //         console.error(`Textarea element with ID "${textareaId}" not found.`);
        //     }
        // });
        //
        //     // Destroy WYSIWYG editor when the modal is hidden
        //     $('#editUserModal').on('hidden.bs.modal', function () {
        //         const userCommentId = $('#editUserModal').data('user-comment-id');
        //         const textareaId = `content-${userCommentId}`;
        //         const textarea = document.getElementById(textareaId);
        //         if (textarea && textarea._wysiwyg) {
        //             textarea._wysiwyg.destroy();
        //             delete textarea._wysiwyg;
        //         }
        //
        //         // Remove the content inside the parent div
        //         const wrapper = document.getElementById('comment_textarea_wrapper');
        //         if (wrapper) {
        //             wrapper.innerHTML = '';
        //
        //             // Re-add the original textarea
        //             const newTextarea = document.createElement('textarea');
        //             newTextarea.name = 'content';
        //             newTextarea.className = 'form-control o_wysiwyg_loader';
        //             newTextarea.minLength = 50;
        //             newTextarea.setAttribute('t-attf-id', 'content-#{str(user_comment_id)}');
        //             wrapper.appendChild(newTextarea);
        //         }
        //     });
    },

    _initializeTooltips: function () {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new Tooltip(tooltipTriggerEl);
        });
    },

    _showErrorMessage: function showErrorNotification(message) {
        this.notification.add(message, {
            title: 'Error',
            sticky: false,
            type: 'danger',
        })
    },

    _showSuccessMessage: function showSuccessNotification(title, message) {
        this.notification.add(message, {
            title: title,
            sticky: false,
            type: 'success',
        });
    },

    _getUsers: async function () {
        try {
            const data = await this.rpc('/cm/manage/users', {});
            if (data.error) {
                this._showErrorMessage(data.error);
            } else {
                this.users = data.users;
                this.filteredUsers = this.users;
                this.countries = data.country_manager_managed_countries;
                this.timezones = data.timezones;
                this.languages = data.languages;
                this._renderUsers();
                this._renderPagination();
            }
        } catch (error) {
            this._showErrorMessage('Error loading users:', error);
        }
    },

    _renderUsers: function () {
        const userContainer = $('#users');
        userContainer.empty();
        const start = (this.currentPage - 1) * this.usersPerPage;
        const end = start + this.usersPerPage;
        const usersToShow = this.filteredUsers.slice(start, end);

        usersToShow.forEach((user, index) => {
            const userRow = `
                <tr data-user-id="${user.id}" class="user_row">
                    <td class="pl-4"> 
                        <span>${start + index + 1}</span>
                    </td>
                    <td>
                        <h5 class="font-medium mb-0 text-nowrap">${user.name}</h5>
                        <span class="text-muted">${user.login}</span>
                    </td>
                    <td>
                        <span class="text-muted">${user.zip && user.city ? `${user.zip} ${user.city}` : '-'}</span><br />
                        <span class="text-muted">${user.country ? user.country : '-'}</span>
                    </td>
                    <td>
                        <span class="text-muted">${user.lang_name ? user.lang_name : ''}</span><br />
                        <span class="text-muted">${user.tz ? user.tz : '-'}</span><br />
                    </td>
                    <td>
                        <span class="badge rounded-pill ${user.active ? 'text-bg-success' : 'text-bg-danger'}">${user.active ? 'ACCOUNT ACTIVE' : 'ACCOUNT INACTIVE'}</span><br />
                        <span class="badge rounded-pill ${user.email_verified ? 'text-bg-success' : 'text-bg-warning'}">${user.email_verified ? 'EMAIL VERIFIED' : 'EMAIL NOT VERIFIED'}</span>
                    </td>
                    <td>
                        <span class="text-muted">${user.create_date ? user.create_date.split(' ')[0] : ''}</span><br />
                        <span class="badge rounded-pill ${user.login_date ? 'text-bg-success' : 'text-bg-info'}">${user.login_date ? 'CONFIRMED LOGIN' : 'NEVER CONNECTED'}</span>
                    </td>
                    <td>
                        <select class="form-control category-select" disabled>
                            <option>Coming soon...</option>
                        </select>
                    </td>
                </tr>
            `;
            userContainer.append(userRow);
        });
    },

    _renderPagination: function () {
        const paginationControls = $('#pagination-controls');
        paginationControls.empty();
        const totalPages = Math.ceil(this.filteredUsers.length / this.usersPerPage);

        for (let i = 1; i <= totalPages; i++) {
            const pageItem = `
                <li class="page-item ${i === this.currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
            paginationControls.append(pageItem);
        }

        paginationControls.find('.page-link').on('click', (event) => {
            event.preventDefault();
            this.currentPage = parseInt($(event.currentTarget).data('page'));
            this._renderUsers();
            this._renderPagination();
        });
    },

    _onSearchInput: function (event) {
        this.searchTerm = $(event.currentTarget).val().toLowerCase();
        this._filterUsers();
    },

    _populateCountryDropdown: function () {
        const countryFilter = $('#countryFilter');
        countryFilter.empty();

        if (this.countries.length > 1) {
            countryFilter.append(new Option('All', 'all'));
        }

        this.countries.forEach(country => {
            countryFilter.append(new Option(country.name, country.id));
        });

        if (this.countries.length === 1) {
            countryFilter.val(this.countries[0].id);
            countryFilter.prop('disabled', true);
        }
    },

    _filterUsers: function () {
    const emailNotVerified = $('#filterEmailNotVerified').is(':checked');
    const neverConnected = $('#filterNeverConnected').is(':checked');
    const accountInactive = $('#filterAccountInactive').is(':checked');
    const searchTerm = this.searchTerm || '';
    const selectedCountry = $('#countryFilter option:selected').text();

    this.filteredUsers = this.users.filter(user => {
        const matchesSearch = user.name.toLowerCase().includes(searchTerm) || user.email.toString().toLowerCase().includes(searchTerm);
        const matchesFilter = (emailNotVerified && !user.email_verified) ||
                              (neverConnected && !user.login_date) ||
                              (accountInactive && !user.active) ||
                              (!emailNotVerified && !neverConnected && !accountInactive);
        const matchesCountry = selectedCountry === 'All' || user.country === selectedCountry;
        return matchesSearch && matchesFilter && matchesCountry;
    });

    this.currentPage = 1;
    this._renderUsers();
    this._renderPagination();
},

    _onEditUserClick: async function (event) {
        const userId = $(event.currentTarget).data('user-id');
        const user = this._getUserById(userId);
        if (user) {
            $('#editUserModal').find('#readonlyUserName').val(user.login);
            $('#editUserModal').find('#editUserName').val(user.name);
            $('#editUserModal').find('#editUserEmail').val(user.email);
            $('#editUserModal').find('#editUserPhone').val(user.phone);
            $('#editUserModal').find('#editUserZip').val(user.zip);
            $('#editUserModal').find('#editUserCity').val(user.city);
            $('#editUserModal').find('#editUserComment').val(user.comment);
            $('#editUserModal').data('user-id', user.id);

            const langField = $('#editUserModal').find('#editUserLang');
            langField.empty();

            this.languages.forEach(language => {
                langField.append(new Option(language.name, language.code, language.code === user.lang));
            });

            langField.val(user.lang);

            const countryField = $('#editUserModal').find('#editUserCountry');
            const userCountryInList = this.countries.some(country => country.name === user.country);

            countryField.empty();
            this.countries.forEach(country => {
                countryField.append(new Option(country.name, country.id, country.name === user.country));
            });

            if (userCountryInList) {
                countryField.val(this.countries.find(country => country.name === user.country).id);
            } else if (this.countries.length > 0) {
                countryField.val(this.countries[0].id);
            }

            const tzField = $('#editUserModal').find('#editUserTz');
            tzField.empty();

            const selectedCountryId = $('#editUserModal').find('#editUserCountry').val();
            const countryTimezones = this.timezones[selectedCountryId] || [];

            if (Array.isArray(countryTimezones) && countryTimezones.length > 0) {
                countryTimezones.forEach(tz => {
                    tzField.append(new Option(tz, tz, tz === user.tz));
                });
            }

            if (user.login_date) {
                $('#editUserModal').find('input:not([type="checkbox"]), select').prop('disabled', true);
                $('#editUserModal').find('.disable-on-readonly').removeClass('text-secondary').addClass('text-muted');
                $('.edite_user_massage_wrapper').removeClass('d-none').show();
            } else {
                $('#editUserModal').find('input, select').prop('disabled', false);
                $('#readonlyUserName, #editUserEmail').prop('disabled', true);
                $('#editUserModal').find('.disable-on-readonly').removeClass('text-muted').addClass('text-secondary');
                $('#saveUserChanges').prop('disabled', false);
                $('.edite_user_massage_wrapper').addClass('d-none').hide();
            }

            // Show or hide the blocked user message based on the user's active status
            if (!user.active) {
                $('#edit_user_modal_send_invite_checkbox').hide();
                $('#edit_user_modal_reset_password_checkbox').hide();
                $('#edit_user_modal_code_of_conduct_checkbox').hide();
                $('#edit_user_modal_disable_user_checkbox').hide();
                $('#edit_user_modal_enable_user_checkbox').show();
                $('#edit_user_modal_show_user_disabled_text').show();
            } else {
                $('#edit_user_modal_send_invite_checkbox').show();
                $('#edit_user_modal_reset_password_checkbox').show();
                $('#edit_user_modal_code_of_conduct_checkbox').show();
                $('#edit_user_modal_disable_user_checkbox').show();
                $('#edit_user_modal_enable_user_checkbox').hide();
                $('#edit_user_modal_show_user_disabled_text').hide();
            }

            $('#editUserModal').modal('show');
        }
    },

    _onCountryChange: function (event) {
        const selectedCountryId = $(event.currentTarget).val();
        this._updateTimezones(selectedCountryId);
    },

    _updateTimezones: function (countryId, selectedTz = null) {
        const tzField = $('#editUserModal').find('#editUserTz');
        tzField.empty();

        const countryTimezones = this.timezones[countryId] || [];

        if (Array.isArray(countryTimezones) && countryTimezones.length > 0) {
            countryTimezones.forEach(tz => {
                tzField.append(new Option(tz, tz, tz === selectedTz));
            });
            if (!selectedTz) {
                tzField.val(countryTimezones[0]);
            }
        } else {
            pytz.all_timezones.forEach(tz => {
                tzField.append(new Option(tz, tz, tz === selectedTz));
            });
        }
    },

    _getUserById: function (userId) {
        return this.users.find(user => user.id === userId);
    },

    _onSaveUserChanges: async function () {
        let sendInvitationEmail = $('#sendInvitationEmail').is(':checked');
        if($('#enableUser').is(':checked'))
            sendInvitationEmail = true;
        const sendResetPasswordEmail = $('#sendResetPasswordEmail').is(':checked');
        const requestCodeOfConduct = $('#requestCodeOfConduct').is(':checked');
        const blockUser = $('#blockUser').is(':checked') && !$('#enableUser').is(':checked');

        const userId = $('#editUserModal').data('user-id');
        const user = this._getUserById(userId);

        const name = $('#editUserName').val();
        const email = $('#editUserEmail').val();
        const phone = $('#editUserPhone').val();
        const zip = $('#editUserZip').val();
        const city = $('#editUserCity').val();
        const country = $('#editUserCountry option:selected').text();
        const tz = $('#editUserTz').val();
        const lang = $('#editUserLang').val();
        const comment = user ? user.comment : '';

        try {
            const data = await this.rpc('/cm/manage/users/edit', {
                send_invitation_email: sendInvitationEmail,
                send_reset_password_email: sendResetPasswordEmail,
                request_code_of_conduct: requestCodeOfConduct,
                block_user: blockUser,
                user_id: userId,
                name: name,
                email: email,
                phone: phone,
                zip: zip,
                city: city,
                country: country,
                tz: tz,
                lang: lang,
                comment: comment
            });

            if (data.error) {
                this._showErrorMessage(data.error);
            } else {
                this._showSuccessMessage(data.title, data.message);
                this._updateLocalUser(userId, name, email, phone, zip, city, country, tz, lang, comment);
                $('#editUserModal').modal('hide');
                await this._getUsers();
            }

            // Uncheck the checkboxes after saving
        $('#sendInvitationEmail').prop('checked', false);
        $('#sendResetPasswordEmail').prop('checked', false);
        $('#requestCodeOfConduct').prop('checked', false);
        $('#blockUser').prop('checked', false);

        } catch (error) {
            this._showErrorMessage('Error saving user:', error);
        }
    },

    _updateLocalUser: function (userId, name, email, phone, zip, city, country, tz, lang, comment) {
        const user = this._getUserById(userId);
        if (user) {
            user.name = name;
            user.email = email;
            user.phone = phone;
            user.zip = zip;
            user.city = city;
            user.country = country;
            user.tz = tz;
            user.lang = lang;
            user.comment = comment;
        }
        this._renderUsers();
    },

    _onCreateUserClick: function () {
        // Clear the form fields
        $('#createUserModal').find('input, select').val('');

         const countryField = $('#createUserModal').find('#createUserCountry');
         //const userCountryInList = this.countries.some(country => country.name === user.country);

            countryField.empty();
            this.countries.forEach(country => {
                countryField.append(new Option(country.name, country.id));
            });

        // Show the modal
        $('#createUserModal').modal('show');
    },

    _onCreateUserChanges: async function () {
        const name = $('#createUserName').val();
        const email = $('#createUserEmail').val();
        const country = $('#createUserCountry').val();

        try {
            const data = await this.rpc('/cm/manage/users/create', {
                name: name,
                email: email,
                country: country,
            });

            if (data.error) {
                this._showErrorMessage(data.error);
            } else {
                this._showSuccessMessage(data.title, data.message);
                await this._getUsers();
                $('#createUserModal').modal('hide');
            }

        } catch (error) {
            this._showErrorMessage(error);
        }
    },
});

export default publicWidget.registry.CountryManager_ManageUsers;
/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.portalEdit = publicWidget.Widget.extend({
    selector: '#profile_tab_profile_pane',
    events: {
        'change #profile_country_select': '_onCountryChange',
        'change #spoken_language_index_select': '_onSpokenLanguageIndexChange',
        'input #spoken_language_search': '_onSpokenLanguageSearch',
        'change #spoken_language_list_select': '_onSpokenLanguageListChange',
        'click #add_spoken_language': '_onAddSpokenLanguage',
        'change .o_forum_file_upload': '_onImageChange',
        'click .o_forum_profile_pic_clear': '_onImageClear',
        'click .remove-language': '_onRemoveSpokenLanguage', // Add event listener for removing spoken language
    },

    init() {
        this._super(...arguments);
        this.rpc = this.bindService("rpc");
        this.notification = this.bindService("notification");
        this.country = "";
        this.states = [];
        this.spoken_languages_index = [];
        this.spoken_languages_list = [];
        this.user_id = $('#user_id').val();
    },

    start: async function () {
        await this._super.apply(this, arguments);
        this._makeSpokenLanguageSortable();
        this._initializeTooltips();
        this._addTop25LanguagesToIndex();
        this._addTop25LanguagesToList();
        this._getSpokedLanguagesIndex();
        this.country = $('#profile_country_select').val();
        if(this.country !== undefined){
            await this._getStates(this.country);
        }
        this._populateSpokenLanguages();

        // Bind validation to form submission
        $('#profile_form').on('submit', (ev) => {
            if (!this._validateSpokenLanguages()) {
                ev.preventDefault();
            }
        });

    },

    _makeSpokenLanguageSortable: function () {
        const spokenLanguageSelect = $('#spoken_language_select');
        spokenLanguageSelect.sortable({
            placeholder: 'ui-state-highlight',
            update: function (event, ui) {
                // Update the hidden input field with the new order
                const sortedLanguages = spokenLanguageSelect.children('li').map(function() {
                    return {
                        name: $(this).data('name'),
                        code: $(this).data('value')
                    };
                }).get();
                $('#hidden_spoken_languages').val(JSON.stringify(sortedLanguages));
            }
        });
        spokenLanguageSelect.disableSelection();
    },

    _populateSpokenLanguages: function () {
        const spokenLanguageSelect = $('#spoken_language_select');
        const noLanguagesMessage = $('#no_languages_message');
        const spokenLanguagesJson = $('#hidden_spoken_languages').val();
        const spokenLanguages = JSON.parse(spokenLanguagesJson);

        spokenLanguageSelect.empty(); // Clear existing items

        if (spokenLanguages.length === 0) {
            noLanguagesMessage.show();
        } else {
            noLanguagesMessage.hide();
            spokenLanguages.forEach(language => {
                const listItem = `<li class="list-group-item cursor-pointer" data-value="${language.code}" data-name="${language.name}">
                                    ${language.name}
                                    <button type="button" class="btn btn-danger btn-sm float-end remove-language">
                                        <i class="fa fa-trash"></i>
                                    </button>
                                  </li>`;
                spokenLanguageSelect.append(listItem);
            });
        }
    },

    _onAddSpokenLanguage: function () {
        const spokenLanguageListSelect = $('#spoken_language_list_select');
        const spokenLanguageSelect = $('#spoken_language_select');
        const noLanguagesMessage = $('#no_languages_message');
        const selectedLanguage = spokenLanguageListSelect.val();
        const selectedLanguageText = spokenLanguageListSelect.find('option:selected').text();

        if (selectedLanguage && !spokenLanguageSelect.find(`li[data-value="${selectedLanguage}"]`).length) {
            const listItem = `<li class="list-group-item cursor-pointer" data-value="${selectedLanguage}" data-name="${selectedLanguageText}">
                ${selectedLanguageText}
                <button type="button" class="btn btn-danger btn-sm float-end remove-language">
                    <i class="fa fa-trash"></i>
                </button>
                </li>`;
            spokenLanguageSelect.append(listItem);

            // Retrieve the current languages from the hidden input
            const currentLanguages = JSON.parse($('#hidden_spoken_languages').val());

            // Add the new language to the list
            currentLanguages.push({
                name: selectedLanguageText,
                code: selectedLanguage
            });

            // Update the hidden input with the new list of languages
            $('#hidden_spoken_languages').val(JSON.stringify(currentLanguages));
            $('#add_spoken_language').prop('disabled', true);

            // Hide the "no languages" message
            noLanguagesMessage.hide();
        }
    },

    _onRemoveSpokenLanguage: function (ev) {
        $(ev.currentTarget).closest('li').remove();

        const spokenLanguageSelect = $('#spoken_language_select');
        const noLanguagesMessage = $('#no_languages_message');
        const sortedLanguages = spokenLanguageSelect.children('li').map(function() {
            return {
                code: $(this).data('value'),
                name: $(this).data('name')
            };
        }).get();

        if (sortedLanguages.length === 0) {
            noLanguagesMessage.show();
        } else {
            noLanguagesMessage.hide();
        }

        $('#hidden_spoken_languages').val(JSON.stringify(sortedLanguages));
    },

    _onCountryChange: async function (ev) {
        const countryId = $(ev.currentTarget).val();
        await this._getStates(countryId);
    },

    _onSpokenLanguageIndexChange: async function (ev) {
        const letter = $(ev.currentTarget).val();
        await this._getSpokedLanguagesByLetter(letter);
    },

    _onSpokenLanguageSearch: function (ev) {
        const searchTerm = $(ev.currentTarget).val().toLowerCase();
        const spokenLanguageListSelect = $('#spoken_language_list_select');
        spokenLanguageListSelect.children('option').each(function () {
            const languageName = $(this).text().toLowerCase();
            if (languageName.includes(searchTerm)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    },

    _onSpokenLanguageListChange: function (ev) {
        const selectedLanguage = $(ev.currentTarget).val();
        const addButton = $('#add_spoken_language');
        const spokenLanguageSelect = $('#spoken_language_select');

        if (selectedLanguage && !spokenLanguageSelect.find(`li[data-value="${selectedLanguage}"]`).length) {
            addButton.prop('disabled', false);
        } else {
            addButton.prop('disabled', true);
        }
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

    _validateSpokenLanguages: function () {
    const spokenLanguagesJson = $('#hidden_spoken_languages').val();
    const spokenLanguages = JSON.parse(spokenLanguagesJson);
    if (spokenLanguages.length === 0) {
        this._showErrorMessage("Please add at least one language.");
        return false;
    }
    return true;
},

    _addTop25LanguagesToIndex: function () {
        const spokenLanguageIndexSelect = $('#spoken_language_index_select');
        spokenLanguageIndexSelect.append(new Option("Most spoken languages", "top25"));
    },

    _addTop25LanguagesToList: async function () {
        const spokenLanguageListSelect = $('#spoken_language_list_select');
        spokenLanguageListSelect.empty();

        try {
            const top25Languages = await this.rpc("/profile/rpc/get_top25_languages");
            if (top25Languages.error) {
                this._showErrorMessage(top25Languages.error);
            } else if (top25Languages.length > 0) {
                top25Languages.forEach(language => {
                    spokenLanguageListSelect.append(new Option(language.name, language.code));
                });
                spokenLanguageListSelect.prop('disabled', false);
            } else {
                spokenLanguageListSelect.append(new Option("None", ""));
                spokenLanguageListSelect.prop('disabled', true);
            }
        } catch (error) {
            console.error('Error fetching top 25 languages:', error);
            spokenLanguageListSelect.prop('disabled', true);
        }
    },

    _getSpokedLanguagesIndex: async function () {
        const spokenLanguageIndexSelect = $('#spoken_language_index_select');
        spokenLanguageIndexSelect.find('option:not([value="top25"])').remove();

            try {
                this.spoken_languages_index = await this.rpc("/profile/rpc/get_languages_index");
                if (this.spoken_languages_index.error) {
                    this._showErrorMessage(this.spoken_languages_index.error);
                } else if (this.spoken_languages_index.length > 0) {
                    this.spoken_languages_index.forEach(letter => {
                        spokenLanguageIndexSelect.append(new Option(letter));
                    });

                    spokenLanguageIndexSelect.prop('disabled', false);
                } else {
                    spokenLanguageIndexSelect.append(new Option("None", ""));
                    spokenLanguageIndexSelect.prop('disabled', true);
                }
            } catch (error) {
                console.error('Error fetching states:', error);
                spokenLanguageIndexSelect.prop('disabled', true);
            }
    },

    _getSpokedLanguagesByLetter: async function (letter) {
        const spokenLanguageListSelect = $('#spoken_language_list_select');
        spokenLanguageListSelect.empty();

            try {
                this.spoken_languages_list = await this.rpc("/profile/rpc/get_languages_by_letter", { letter: letter });
                if (this.spoken_languages_list.error) {
                    this._showErrorMessage(this.spoken_languages_list.error);
                } else if (this.spoken_languages_list.length > 0) {
                    this.spoken_languages_list.forEach(language => {
                        spokenLanguageListSelect.append(new Option(language.name, language.code));
                    });

                    spokenLanguageListSelect.prop('disabled', false);
                } else {
                    spokenLanguageListSelect.append(new Option("None", ""));
                    spokenLanguageListSelect.prop('disabled', true);
                }
            } catch (error) {
                console.error('Error fetching states:', error);
                spokenLanguageListSelect.prop('disabled', true);
            }
    },

    _getStates: async function (countryId) {
        const stateSelect = $('#profile_state_select');
        stateSelect.empty();
        if (countryId) {
            try {
                this.states = await this.rpc("/profile/rpc/get_states" ,{ country_id: countryId });
                if (this.states.error) {
                    this._showErrorMessage(this.states.error);
                } else if (this.states.length > 0) {
                    this.states.forEach(state => {
                        stateSelect.append(new Option(state.name, state.id));
                    });

                    stateSelect.prop('disabled', false);
                } else {
                    stateSelect.append(new Option("None", ""));
                    stateSelect.prop('disabled', true);
                }
            } catch (error) {
                console.error('Error fetching states:', error);
                stateSelect.prop('disabled', true);
            }
        } else {
            stateSelect.append(new Option("None", ""));
            stateSelect.prop('disabled', true);
        }
    },

    _onImageChange: function (ev) {
        const input = ev.currentTarget;
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = (e) => {
                $('#profile_avatar_img').attr('src', e.target.result);
            };
            reader.readAsDataURL(input.files[0]);
        }
    },

    _onImageClear: async function (ev) {
        ev.preventDefault();
        // Clear the file input
        $('.o_forum_file_upload').val('');

        // Remove the current image from the img tag
        $('#profile_avatar_img').attr('src', '');

        // Send an RPC request to the backend to remove the current image and generate a new one
        try {
            const response = await this.rpc("/profile/rpc/clear_image", {});

            if (response.success) {
                // Update the img tag with the new image
                $('#profile_avatar_img').attr('src', response.new_image_url);
            } else {
                console.error('Error clearing image:', response.error);
            }
        } catch (error) {
            console.error('Error clearing image:', error);
        }
    }
});

return publicWidget.registry.portalEdit;
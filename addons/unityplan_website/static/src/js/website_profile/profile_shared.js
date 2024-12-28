/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.portalDetails = publicWidget.Widget.extend({
    selector: '#profile_extra_info_tablist',
    start: function () {
        this._super.apply(this, arguments);
        this._initializeTabsWithoutBootstrap();
        window.onpopstate = (event) => {
            this._initializeTabsWithoutBootstrap();
        };
    },
    _initializeTabsWithoutBootstrap: function () {
        const tabs = document.querySelectorAll('#profile_extra_info_tablist a');
        const tabPanes = document.querySelectorAll('.tab-pane');

        tabs.forEach(tab => {
            tab.addEventListener('click', function (event) {
                event.preventDefault();

                // Remove active class from all tab panels
                tabPanes.forEach(pane => pane.classList.remove('active'));

                // Add active class to corresponding panel
                const activePaneId = tab.getAttribute('href').substring(1);
                const activePane = document.getElementById('profile_tab_'+activePaneId+'_pane');
                if (activePane) {
                    activePane.classList.add('active');
                }
            });
        });

        // Default to "Profile" tab if no active tab or URL hash
        const hash = window.location.hash;
        if (hash) {
            const activeTab = document.querySelector(`a[href="${hash}"]`);
            if (activeTab) {
                activeTab.click();
            }
        } else {
            const newsTab = document.querySelector('#profile_extra_info_tablist a[href="#profile"]');
            if (newsTab && !document.querySelector('.tab-pane.active')) {
                newsTab.click();
            }
        }
    },
});

return publicWidget.registry.portalDetails;
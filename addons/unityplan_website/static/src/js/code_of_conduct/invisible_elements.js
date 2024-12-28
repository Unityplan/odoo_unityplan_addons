/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.codeOfConductInvisibleElements = publicWidget.Widget.extend({
    selector: '#oe_structure_code_of_conduct_first_visit',
    events: {},

    init() {
        this._super(...arguments);
    },

    start: function () {
        this._super.apply(this, arguments);
        const element = this.$el;
        console.log('element', element);

        const updateVisibility = () => {
            const invisible = element[0].hasAttribute('data-invisible');
            if (invisible) {
                element.addClass('d-none');
            } else {
                element.removeClass('d-none');
            }
        };

        // Initial check
        updateVisibility();

        // Observe changes to the data-invisible attribute
        const observer = new MutationObserver(() => {
            updateVisibility();
        });

        observer.observe(element[0], {
            attributes: true,
            attributeFilter: ['data-invisible']
        });
    },
});

return publicWidget.registry.codeOfConductInvisibleElements;
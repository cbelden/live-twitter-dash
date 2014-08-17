define([
    'jquery',
    'underscore',
    'backbone',
    'text!templates/navbar.html',
    'views/modal-view'
], function($, _, Backbone, NavbarTemplate, ModalView) {
    var NavbarView = Backbone.View.extend({
        el: $('.navbar'),

        greyOut: function() {
            return $('.grey-out');
        },

        initialize: function() {
            // Render the navbar
            this.$el.html(_.template(NavbarTemplate));

            // Create the modal menu view
            this.modalView = new ModalView();
        },

        events: {
            'click .toggle-menu': 'onToggleMenu',
        },

        onToggleMenu: function() {
            var isVisible = this.modalView.$el.css('display') !== 'none';
            var newDisplay = isVisible ? 'none' : 'inherit';
            this.modalView.$el.css('display', newDisplay);
            this.greyOut().css('display', newDisplay);
        }

    });

    return NavbarView;
});
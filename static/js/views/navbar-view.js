define([
    'jquery',
    'underscore',
    'backbone',
    'text!templates/navbar.html',
    'views/modal-view'
], function($, _, Backbone, NavbarTemplate, ModalView) {
    return Backbone.View.extend({

        el: '.navbar',

        $greyOut: function() {
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
            'click .play-nav': 'onPlayStream',
            'click .pause-nav': 'onPauseStream',
        },

        onToggleMenu: function(ev) {
            ev.preventDefault();
            var isVisible = this.modalView.$el.css('display') !== 'none';
            var newDisplay = isVisible ? 'none' : 'inherit';
            this.modalView.$el.css('display', newDisplay);
            this.$greyOut().css('display', newDisplay);
        },

        onPlayStream: function(ev) {
            ev.preventDefault();
            this.modalView.onPlayStream(ev, true);
        },

        onPauseStream: function(ev) {
            ev.preventDefault();
            this.modalView.onPauseStream(ev);
        },

    });
});
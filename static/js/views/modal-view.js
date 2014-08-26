define([

    'jquery',
    'underscore',
    'backbone',
    'socket/socket',
    'views/filter-list-view',
    'text!templates/menu.html',

], function($, _, Backbone, socket, FilterListView, MenuTemplate) {
    return Backbone.View.extend({

        el: '#menu',

        tweets: function() {
            return $('.tweets');
        },

        tweetTitle: function() {
            return $('.container .title-bar h2');
        },

        greyOut: function() {
            return $('.grey-out');
        },

        newFilter: function() {
            return $('.filter-input');
        },

        initialize: function() {
            // Subviews
            this.filterListView = new FilterListView();
            this.render();
        },

        render: function() {
            // Render this view
            this.$el.html(_.template(MenuTemplate));

            // Render subview
            this.filterListView.setElement(this.$('#filters'));
        },

        events: {
            'click .start': 'onPlayStream',
            'click .pause': 'onPauseStream',
            'click .toggle-menu': 'onToggleMenu',
            'keyup .filter-input': 'onEnterAddTerm',
            'click .add-filter': 'onAddFilter',
            'click .clear': 'onClearStream',
        },

        onPlayStream: function() {
            var terms = this.filterListView.collection.pluck('term');

            socket.emit('start-stream', {tracking: terms});
            this.onToggleMenu();
            this.displayTerms(terms);
        },

        onPauseStream: function() {
            socket.emit('pause-stream');
        },

        onToggleMenu: function() {
            var isVisible = this.$el.css('display') !== 'none';
            var newDisplay = isVisible ? 'none' : 'inherit';
            this.$el.css('display', newDisplay);
            this.greyOut().css('display', newDisplay);
        },

        onEnterAddTerm: function(ev) {
            if (ev.keyCode == 13) {
                this.onAddFilter();
            }
        },

        onAddFilter: function() {
            //  Add the new filter term to the collection
            var newTermTextarea = this.newFilter();
            var newTerm = {term: this.newFilter().val().trim()};
            this.filterListView.collection.add(newTerm);

            // Empty the input textarea
            this.newFilter().val('');
        },

        onClearStream: function() {
            this.tweets().empty();
        },

        displayTerms: function() {
            var termsText = '';
            var terms = this.filterListView.collection.pluck('term');

            _.each(terms, function(term) {
                termsText += term + ', ';
            });

            this.tweetTitle().text('Stream Filtering on: [' + termsText.slice(0, -2) + ']');
        },
    });
});
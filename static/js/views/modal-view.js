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

        $tweets: function() {
            return $('.tweets');
        },

        $tweetTitle: function() {
            return $('.container .title-bar h2');
        },

        $greyOut: function() {
            return $('.grey-out');
        },

        $newFilter: function() {
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

        onPlayStream: function(ev, skipToggle) {
            var terms = this.filterListView.collection.pluck('term');
            ev.preventDefault();
            socket.emit('start-stream', {tracking: terms});

            if (!skipToggle) {
                this.onToggleMenu(ev);
            }

            this.setTitle('Filtering', terms);
        },

        onPauseStream: function(ev) {
            var terms = this.filterListView.collection.pluck('term');
            ev.preventDefault();
            socket.emit('pause-stream');
            this.setTitle('Paused', terms);
        },

        onToggleMenu: function(ev) {
            var isVisible = this.$el.css('display') !== 'none';
            var newDisplay = isVisible ? 'none' : 'inherit';
            ev.preventDefault();
            this.$el.css('display', newDisplay);
            this.$greyOut().css('display', newDisplay);
        },

        onEnterAddTerm: function(ev) {
            ev.preventDefault();

            // Intercept 'Enter' key
            if (ev.keyCode == 13) {
                this.onAddFilter(ev);
            }
        },

        onAddFilter: function(ev) {
            var newTermTextarea = this.$newFilter();
            var newTerm = {term: this.$newFilter().val().trim()};
            ev.preventDefault();

            //  Add the new filter term to the collection
            this.filterListView.collection.add(newTerm, {add: true, validate: true});

            // Empty the input textarea
            this.$newFilter().val('');
        },

        onClearStream: function(ev) {
            ev.preventDefault();
            this.$tweets().empty();
        },

        setTitle: function(state, terms) {
            var termsText = '';

            _.each(terms, function(term) {
                termsText += term + ', ';
            });

            this.$tweetTitle().text('Stream ' + state + ' on: [' + termsText.slice(0, -2) + ']');
        },
    });
});
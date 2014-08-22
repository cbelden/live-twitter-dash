define([
    'jquery',
    'underscore',
    'backbone',
    'socket/socket',
    'text!templates/menu.html',
], function($, _, Backbone, socket, MenuTemplate) {
    var ModalView = Backbone.View.extend({
        el: '#menu',

        tweets: function() {
            return $('.tweets');
        },

        newFilter: function() {
            return $('.filter-input');
        },

        filters: function() {
            return $('.filter');
        },

        filterContainer: function() {
            return $('.filters');
        },

        tweetTitle: function() {
            return $('.container .title-bar h2');
        },

        greyOut: function() {
            return $('.grey-out');
        },

        initialize: function() {
            //TODO: need to render the menu template and any other child templates
            this.$el.html(_.template(MenuTemplate));
        },

        events: {
            'click .start': 'onPlayStream',
            'click .pause': 'onPauseStream',
            'click .toggle-menu': 'onToggleMenu',
            'keyup .filter-input': 'onEnterAddTerm',
            'click .add-term': 'onAddTerm',
            'click .delete-filter': 'onDeleteTerm',
            'click .clear': 'onClearStream',
        },

        onPlayStream: function() {
            var terms = function() {  // Not sure if this is good style.. could extract this to an object method and call this.getFilterTerms()
                var terms = [];
                $(".filter").each(function() {
                    terms.push($(this).text());
                });
                return terms;
            }();

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
                this.onAddTerm();
            }
        },

        onAddTerm: function() {
            var newTermTextarea = this.newFilter();
            var newTerm = this.newFilter().val().trim();
            this.newFilter().val('');

            if (this.validateNewTerm(newTerm)) {
                // TODO starting to think the filters should be a subview.... going to hardcode this shit for now
                newFilter = '<div class="filter">' + newTerm + '<div class="delete-filter button"><img src="static/img/close-icon.png"></div></div>';

                // Limit filter terms to 5
                var filterLength = $(".filter").length;

                if (filterLength > 4) {
                    $(".filter:last-child").remove();
                }

                this.filterContainer().prepend(newFilter);

                // Delete current textarea text
                newTermTextarea.value = '';
            }
            else {
                alert("Hey MOFO! New filter terms must not be empty, unique, and only contain letters and numbers.");
            }
        },

        onDeleteTerm: function(ev) {
            console.log(ev.target);
            // Check if ending element is the nested img
            if (ev.target.tagName.toLowerCase() === 'img') {
                $(ev.target).parent().parent().remove();
            }
            else {
                $(ev.target).parent().remove();
            }
        },

        onClearStream: function() {
            this.tweets().empty();
        },

        displayTerms: function() {
            var termsText = '';

            this.filters().each( function() {
                termsText += $(this).text() + ', ';
            });

            this.tweetTitle().text('Stream Filtering on: [' + termsText.slice(0, -2) + ']');
        },

        validateNewTerm: function(newTerm) {
            var isValid = true;

            if (!newTerm) {
                isValid = false;
            }

            // Eliminate all non-letter and non-number characters
            if (newTerm.replace(/\W+/g, "") !== newTerm) {
                isValid = false;
            }

            // Check that filter has not already been added
            this.filters().each(function() {
                var prevTerm = $(this).text();
                if (prevTerm == newTerm) {
                    isValid = false;
                }
            });

            return isValid;
        },
    });

    return ModalView;
});
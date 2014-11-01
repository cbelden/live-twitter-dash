define([

    'jquery',
    'underscore',
    'backbone',
    'text!templates/tweet.html',

], function($, _, Backbone, TweetTemplate) {

    return Backbone.View.extend({

        el: $('#tweets'),

        initialize: function() {
            // Create collection and add a handler to the add event
            this.collection = new Backbone.Collection();
            this.collection.bind('add', this.onTweetAdded, this);
        },

        onTweetAdded: function() {
            // Compile the tweet template w/ the new data
            var model = _.last(this.collection.models).toJSON();
            var template = _.template(TweetTemplate, model);
            this.$el.prepend(template);
            this.slideDownTweet();
        },

        slideDownTweet: function() {
            var newTweet = $('.twitter-data.hidden');
            console.log(newTweet);

            setTimeout(function() {
                newTweet.removeClass('hidden').addClass('visible');
            }, 20);
        }

    });
});

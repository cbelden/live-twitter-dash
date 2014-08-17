define([
    'backbone',
    'underscore',
    'models/tweet-model',
], function(Backbone, _, TweetModel) {

    return Backbone.Collection.extend({
        model: TweetModel,
    });
});
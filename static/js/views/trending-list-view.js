define([

    'jquery',
    'underscore',
    'backbone',
    'collections/trending-collection',
    'text!templates/trending-term.html',

], function($, _, Backbone, TrendingCollection, TrendingTemplate) {
    return Backbone.View.extend({
        initialize: function() {
            // Create the trending terms collection
            this.collection = new TrendingCollection();
        },

        render: function() {
            // Populate the collection and render each term
            var that = this;
            that.collection.fetch({success: function() {
                that.collection.each(function(model) {
                var template = _.template(TrendingTemplate, model.toJSON());
                that.$el.append(template);
                });
            }});
        },
    });
});
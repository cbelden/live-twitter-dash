define([

    'backbone',

], function(Backbone) {

    return Backbone.Model.extend({

        idAttribute: '_id',
        
        validate: function(attrs, options) {
            var nonAlphanumeric = /\W/;

            // Input must be non-empty and all word characters.
            if (!attrs.term) return "Need to specify a term.";
            if (attrs.term.match(nonAlphanumeric)) return "Please use alphanumeric characters when adding a new filter.";

            // Limit # of filters to 5
            if (options.collection && options.collection.length > 4) return "Please delete a filter before adding more.";
        },
    });
});
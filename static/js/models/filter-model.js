define([

    'backbone',

], function(Backbone) {

    return Backbone.Model.extend({

        idAttribute: '_id',
        
        validate: function(attrs) {
            var nonalphanumeric = /\W/;

            if (!attrs.term) {
                return "Need to specify a term.";
            }

            if (attrs.term.match(nonAlphanumeric)) {
                return "Please use alphanumeric characters when adding a new filter.";
            }
        },
    });
});
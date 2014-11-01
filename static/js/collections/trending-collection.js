define([

    'backbone',

], function(Backbone) {

    return Backbone.Collection.extend({
        url: '/trending-terms',

        parse: function(resp) {
            return resp.results;
        }
    });
});
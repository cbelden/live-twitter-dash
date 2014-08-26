define([

    'underscore',
    'jquery',
    'backbone',
    'models/filter-model',

], function(_, $, Backbone, FilterModel) {

    return Backbone.Collection.extend({
        model: FilterModel,
    });
});
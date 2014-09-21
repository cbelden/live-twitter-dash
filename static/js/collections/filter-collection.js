define([

    'backbone',
    'models/filter-model',

], function(Backbone, FilterModel) {

    return Backbone.Collection.extend({
        model: FilterModel,
    });
});
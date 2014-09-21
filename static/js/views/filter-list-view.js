define([

    'jquery',
    'underscore',
    'backbone',
    'collections/filter-collection',
    'text!templates/filter.html',

], function($, _, Backbone, FilterCollection, FilterTemplate) {

    return Backbone.View.extend({

        events: {
            'click .delete-filter': 'onDeleteFilter',
        },

        initialize: function() {
            this.collection = new FilterCollection();
            this.collection.bind('add', this.onFilterAdded, this);
        },

        onFilterAdded: function() {
            var model = _.last(this.collection.models);
            var term = model.toJSON();
            term.id = model.cid;

            var template = _.template(FilterTemplate, term);
            this.$el.prepend(template);

            // Cap # of filters
            if (this.collection.length > 5) {
                // TODO delete the last filter. Limit input to 5 terms.
            }
        },

        onDeleteFilter: function(ev) {
            var parent = $(ev.target).parent();
            ev.preventDefault();

            while (parent.attr('class') !== 'filter') {
                parent = parent.parent();
            }

            this.collection.remove(parent.attr('data-id'));
            $(parent).remove();
        },
    });
});
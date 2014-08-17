define([
    'jquery',
    'backbone',
    'underscore',
    'socket/socket-router'
], function($, Backbone, _, SocketRouter) {

    var App = {
        start: function() {
            SocketRouter.initialize();
        },
    };

    return App;
});
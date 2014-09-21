define([
    'backbone',
    'views/tweet-list-view',
    'views/navbar-view',
    'socket/socket',
], function(Backbone, TweetListView, NavView, socket) {
    
    var SocketRouter = {
        initialize: function() {
            var tweetListView = new TweetListView();
            var navView = new NavView();

            /* Socket event handlers */
            socket.on('connect', function() {
                console.log('socketio connected to the server.');
            });

            socket.on('disconnect', function() {
                console.log('socketio disconnected from the server.');
            });

            socket.on('twitter-data', function(tweet) {
                console.log('Received twitter data from the server.');
                var model = _.last(tweetListView.collection.models);
                tweetListView.collection.add(tweet.data);
            });
        },
    };
    
    return SocketRouter;
});
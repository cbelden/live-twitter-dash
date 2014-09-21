// Configure shortcut aliases
require.config({
    paths: {
        jquery: 'libs/jquery/jquery-2.1.1.min',
        underscore: 'libs/underscore/underscore-min',
        backbone: 'libs/backbone/backbone-min',
        socketio: [
                'http://cdnjs.cloudflare.com/ajax/libs/socket.io/0.9.16/socket.io.min',
                'libs/socketio/socket.io'
                ],
        templates: '../templates'
    }
});

// Bootstrap our app
define(['app'], function(App) {
    $(document).ready( App.start );
});
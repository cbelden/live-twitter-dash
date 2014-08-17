define([
    'socketio'
], function(io) {

    // Return the socketio connection
    return io.connect('/twitter');
});
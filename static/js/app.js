var app = angular.module('TwitterStreamApp', ['ngAnimate']);

// Navbar controller
app.controller('NavbarController', ['$scope', 'Modal', 'TweetStream', function($scope, Modal, TweetStream) {
    $scope.toggleMenu = function() {
        Modal.toggle();
    };

    $scope.playStream = function() {
        TweetStream.play();
    };

    $scope.pauseStream = function() {
        TweetStream.pause();
    };
}]);

// Modal controller
app.controller('ModalController', ['$scope', 'Modal', function($scope, Modal) {
    $scope.isShown = function() {
        return Modal.isShown;
    };
}]);

// Menu controller
app.controller('MenuController', ['$scope', 'Socket', 'TweetStream', 'Modal', function($scope, socket, TweetStream, Modal) {
    $scope.model = {
        terms:      TweetStream.terms,
        newTerm:    '',
    };

    $scope.addTerm = function(newTerm) {
        var error = TweetStream.addFilter(newTerm);
        if (error) alert(error);
        else $scope.model.newTerm = '';
    };

    $scope.deleteTerm = function(idx) {
        TweetStream.deleteFilter(idx);
    };

    $scope.playStream = function() {
        if ($scope.model.terms.length > 0) {
            TweetStream.play();
            $scope.closeModal();
        }
        else {
            alert('Add some terms first!');
        }
    };

    $scope.pauseStream = function() {
        TweetStream.pause();
    };

    $scope.clearStream = function() {
        TweetStream.clear();
    };

    $scope.closeModal = function() {
        Modal.toggle();
    };
}]);

// Tweet Stream controller
app.controller('TweetStreamController', ['$scope', 'TweetStream', function($scope, TweetStream) {
    $scope.model = {
        tweets: TweetStream.tweets,
    };
}]);

// Tweet service. Handles all communication to the server for play/pause requests. Manages
// the terms used for filtering the stream.
app.factory('TweetStream', ['$log', 'Socket', 'FilterList', function($log, socket, FilterList) {
    var tweets = [];
    var prevTerms = [];

    // Subscribe to socket events
    socket.on('twitter-data', function(tweet) {
        $log.log('ading a new tweet, tight');
        tweets.unshift(tweet);
    });

    return {
        tweets: tweets,

        terms: FilterList.terms,

        clear: function() {
            tweets.length = 0;
        },

        play: function() {
            if (this.terms.length === 0) {
                alert('Please enter some filtering terms first!');
                return;
            }

            socket.emit('start-stream', {tracking: this.terms});
        },

        pause: function() {
            socket.emit('pause-stream');
        },

        addFilter: function(term) {
            return FilterList.add(term);
        },

        deleteFilter: function(idx) {
            FilterList.remove(idx);
        },

    };
}]);

// Socket Service (copied from http://www.html5rocks.com/en/tutorials/frameworks/angular-websockets/)
app.factory('Socket', ['$rootScope', function($rootScope) {
    var socket = io.connect('/twitter');

    return {
        on: function(eventName, callback) {
            socket.on(eventName, function() {
                var args = arguments;
                $rootScope.$apply(function() {
                    callback.apply(socket, args);
                });
            });
        },

        emit: function(eventName, data, callback) {
            socket.emit(eventName, data, function() {
                var args = arguments;
                $rootScope.$apply(function() {
                    if (callback) {
                        callback.apply(args);
                    }
                });
            });
        },
    };
}]);

// Filter term service
app.factory('FilterList', [function() {
    var terms = [];
    var validate = function(newTerm, terms) {
        // Valid terms are non-empty, alphanumeric, and unique
        return newTerm &&
               newTerm.match(/^[1-9a-zA-Z]+$/g) &&
               (terms.length === 0 || terms.indexOf(newTerm) === -1);
    };

    return {
        add: function(newTerm) {
            if (terms.length < 6 && validate(newTerm, terms)) {
                terms.unshift(newTerm);
            }
            else {
                return 'Could not add a new tweet.';
            }
        },

        remove: function(idx) {
            return terms.splice(idx, 1)[0];
        },

        terms: terms,
    };
}]);

// Modal manager. Handles toggling the display of modals
app.factory('Modal', [function() {
    return {
        isShown: true,

        toggle: function() {
            this.isShown = !this.isShown;
        }
    };
}]);


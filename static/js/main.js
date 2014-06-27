$(document).ready(function() {

	// Connect to the server's iosocket
	// var socket = io.connect('http://localhost:5000');
	var socket = io.connect('http://' + document.domain + ':' + location.port + '/twitter');

	// Get handles for twitter widget container
	var twitter_container = $('.twitter-container');

	// Define on connect data
	socket.on('connect', function() {
		console.log("Client connected to server via socketio.");
	});

	// Define event for Twitter container
	socket.on('twitter-data', function(msg) {

		// Get Tweet information
		var screenName = '<strong>' + msg.data.screen_name + '</strong>: ';
		var text = screenName + msg.data.text;
		var url = msg.data.user_image_url;

		console.log("[socket.io] Received new twitter data.");

		// Construct html
		var img = '<div class="profile-image"><img src="' + url + '"></div>';
		var tweet = '<div class="tweet-text">' + text + '</div>';
		var tweetData = $('<div class="twitter-data">' + img + tweet + '</div>');

		// Append tweet to twitter widget
		tweetData.css('display', 'none');
		twitter_container.prepend(tweetData);
		tweetData.slideDown(1000);

		// Delete older tweets
		var $articleCount = $('.twitter-data').length;
		while ($articleCount > 10) {
			$('.twitter-data:last-child').remove();
			$articleCount = $('.twitter_data').length;
		}
	});
});

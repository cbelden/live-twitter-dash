$(document).ready(function() {

	// Connect to the server's iosocket
	// var socket = io.connect('http://localhost:5000');
	var socket = io.connect('http://' + document.domain + ':' + location.port + '/twitter');

	// Get handles for twitter widget container
	var twitter_container = $('.tweets');

    // Define on connect handler
    socket.on('connect', function() {
        console.log("Client connected to server via socketio.");
    });

    // Define on disconnect handler
    socket.on('disconnect', function() {
        console.log("Socketio client disconnected to server.");
    });

	// Define event for Twitter container
	socket.on('twitter-data', function(msg) {

		// Get Tweet information
		var screenName = '<strong>' + msg.data.screen_name + '</strong>: ';
		var text = screenName + msg.data.text;
		var img_url = msg.data.image_url;
        var tweet_url = msg.data.tweet_url;

		console.log("[socket.io] Received new twitter data.");

		// Construct tweet element
		var img = '<img src="' + img_url + '">';
        var tweetLink = '<a href="' + tweet_url + '" target="blank">' + img + '</a>';
        var profImage = '<div class="profile-image">' + tweetLink + '</div>';
		var tweet = '<div class="tweet-text">' + text + '</div>';
		var tweetData = $('<div class="twitter-data">' + profImage + tweet + '</div>');

		// Append tweet to twitter widget
		tweetData.css('display', 'none');
		twitter_container.prepend(tweetData);
		tweetData.slideDown(1000);

		// Delete older tweets
		var articleCount = $('.twitter-data').length;
		while (articleCount > 50) {
			$('.twitter-data:last-child').remove();
			articleCount = $('.twitter_data').length;
		}
	});

    // Set menu bar animation
    var toggleMenu = function() {
        var optionsMenu = $(".options-menu");

        if (optionsMenu.css('display') === 'none') {
            optionsMenu.slideDown();
            $(".grey-out").css('display', 'inherit');
        }
        else {
            optionsMenu.slideUp();
            $(".grey-out").css('display', 'none');
        }
    };

    var menuButton = $(".menu-button");

    menuButton.click(function() {
        toggleMenu();
    });

    $(".close-menu").click(function() {
        toggleMenu();
    });

    // Handle the add filter event
    var addFilterButton = $(".add-filter");

    // Define the addFilter method; adds a filter to the filters div.
    var addFilter = function() {
        var filters = $(".filters");
        var textArea = document.getElementsByClassName("filter-input")[0];
        var newFilter = textArea.value;

        if (newFilter) {

            // Ensure the input is valid and not malicious
            var validInput = true;

            // Eliminate all non-letter and non-number characters
            if (newFilter.replace(/\W+/g, "") !== newFilter) {
                validInput = false;
            }

            // Check that filter has not already been added
            $(".filter").each(function() {
                var prevFilter = $(this).text();
                if (prevFilter === newFilter) {
                    validInput = false;
                }
            });

            // Add filter to the filters div
            if (validInput) {
                newFilter = '<div class="filter">' + newFilter + '<div class="delete-filter button"><img src="static/img/close-icon.png"></div>' + '</div>';

                // Limit filter terms to 5
                var filterLength = $(".filter").length;

                if (filterLength > 4) {
                    $(".filter:last-child").remove();
                }

                filters.prepend(newFilter);

                // Delete current textarea text
                textArea.value = '';
            }

            else {
                alert("Invalid filter. No repeats. No non-alphanumeric characters.");
            }
        }
    };

    addFilterButton.click(addFilter);

    // Handle the delete filter event
    var deleteFilterButton = $(".delete-filter");

    // Note: this pattern found at http://stackoverflow.com/questions/8191064/jquery-on-function-for-future-elements-as-live-is-deprecated
    // and describes how to add events to 'future' elements. The delete filter buttons
    // do not exist on the "page ready" event.
    $(".filters").on("click", ".delete-filter", function() {
        $(this).parent().remove();
    });

    // Handle the Start stream event
    var startButton = $(".start-stream");

    startButton.click(function() {

        var terms = [];

        // Collect all of the filter terms
        $(".filter").each(function() {
            terms.push($(this).text());
        });

        // Emit a socketio event to the client to start a stream
        if (terms.length > 0) {
            socket.emit('start-stream', {'tracking': terms});
            // Hide menu
            toggleMenu();

            // Show the tracking items on container title
            var termsText = "";
            for (var i=0, item; item=terms[i]; i++) {
                termsText += item + ", ";
            }

            termsText = termsText.slice(0, -2);

            $(".container .title-bar h2").text('Stream- Filtering on [' + termsText + ']');
        }
        else {
            alert("You need to specify some tracking terms!");
        }
    });

    // Handle the Pause stream event
    $(".pause-stream").click(function() {
        socket.emit('pause-stream');
    });

    // Handle clear stream event
    $(".clear-stream").click(function() {
        $(".twitter-data").each(function() {
            $(this).slideUp();
        });
    });

    // Handle enter event when menu is open: There is a better way to to this. set add filter button to in focus.
    $(document).keypress(function (e) {

        // If the key is "ENTER"
        if (e.which == 13) {

            // Prevent enter button from being pressed.
            e.preventDefault();
            
            if ($(".options-menu").css('display') !== 'none') {
                addFilterButton.click();
            }
        }
    });
});

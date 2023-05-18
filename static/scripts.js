function loadHistory() {
    const history = JSON.parse(localStorage.getItem("history")) || [];
    history.forEach(item => {
        addReviewToList(item.restaurant, item.review, item.sentiment);
    });
    const restaurants = JSON.parse(localStorage.getItem("restaurants")) || [];
    restaurants.forEach(restaurant => {
        if ($('#restaurant-filter option').filter(function() {
            return this.text === restaurant;
        }).length === 0) {
            $('#restaurant-filter').append(new Option(restaurant, restaurant));
        }
    });
}

// Save the review history and restaurant list to LocalStorage
function saveHistory() {
    const history = [];
    $("#history .list-group-item").each(function () {
        const restaurant = $(this).find(".restaurant-name").text();
        const review = $(this).find(".review-text").text();
        const sentiment = $(this).find(".sentiment-indicator").text() === "😊" ? 1 : -1;
        history.push({restaurant, review, sentiment});
    });
    localStorage.setItem("history", JSON.stringify(history));
    const restaurants = [];
    $("#restaurant-filter option").each(function () {
        restaurants.push($(this).val());
    });
    localStorage.setItem("restaurants", JSON.stringify(restaurants));
}


function analyze() {
    $("#result").text(""); // Clear the old message
    const review = $("#review").val();
    const restaurant = $("#restaurant").val();
    $.post("/analyze", {review: review, restaurant: restaurant}, function (data) {
        $("#result").text(data.sentiment > 0 ? "😊" : "☹️");
        // Add the new review to the history
        const listItem = `
            <li class="list-group-item">
                <strong>Restaurant:</strong> <span class="restaurant-name">${restaurant}</span><br>
                <strong>Review:</strong> ${review} <br>
                <strong>Sentiment:</strong> <span class="sentiment-indicator">${data.sentiment > 0 ? "😊" : "☹️"}</span>
            </li>`;
        $("#history").append(listItem);
        // Add the restaurant to the filter list if not already present
        if ($('#restaurant-filter option').filter(function() {
            return this.text === restaurant;
        }).length === 0) {
            $('#restaurant-filter').append(new Option(restaurant, restaurant));
        }
        // Clear the form
        $("#review").val("");
        $("#restaurant").val("");
        displaySentimentCount();  // update sentiment count after adding a review
    }).fail(function () {
        $("#result").text("Error");
    });
    saveHistory();
}

function countSentiments() {
    let posCount = 0;
    let negCount = 0;
    const restaurant = $("#restaurant-filter").val();
    $("#history .list-group-item").each(function () {
        const itemRestaurant = $(this).find(".restaurant-name").text();
        if (restaurant === "" || itemRestaurant === restaurant) {
            const sentiment = $(this).find(".sentiment-indicator").text();
            sentiment === "😊" ? posCount++ : negCount++;
        }
    });
    return [posCount, negCount];
}

function displaySentimentCount() {
    const selectedRestaurant = $("#restaurant-filter").val();
    let positiveCount = 0;
    let negativeCount = 0;
    $("#history .list-group-item").each(function () {
        if ($(this).is(':visible')) {
            const sentiment = $(this).find(".sentiment-indicator").text();
            const restaurant = $(this).find(".restaurant-name").text();
            if (selectedRestaurant === "" || selectedRestaurant === restaurant) {
                if (sentiment === "😊") {
                    positiveCount += 1;
                } else if (sentiment === "☹️") {
                    negativeCount += 1;
                }
            }
        }
    });
    const totalReviews = positiveCount + negativeCount;
    if (totalReviews > 0) {
        const positivePercentage = Math.round((positiveCount / totalReviews) * 100);
        const negativePercentage = 100 - positivePercentage;
        const sentimentCountText = `
            Positive Reviews: ${positiveCount} (${positivePercentage}%) <br>
            Negative Reviews: ${negativeCount} (${negativePercentage}%)
        `;
        $("#sentiment-count").html(sentimentCountText);
    } else {
        $("#sentiment-count").html("");
    }
}

// The rest of the scripts.js code remains the same...

function filterReviews() {
    const restaurant = $("#restaurant-filter").val();
    $("#history .list-group-item").each(function () {
        const itemRestaurant = $(this).find(".restaurant-name").text();
        if (restaurant === "" || itemRestaurant === restaurant) {
            $(this).show();
        } else {
            $(this).hide();
        }
    });
    displaySentimentCount();  // update sentiment count after filtering
}

$(document).ready(function () {
    $("#submit").on("click", analyze);
    $("#restaurant-filter").change(function () {
        filterReviews();
        displaySentimentCount();
    });
});
function analyze() {
    $("#result").text(""); // Clear the old message
    const review = $("#review").val();
    $.post("/analyze", {review: review}, function (data) {
        console.log(data);
        $("#result").text(data.prediction > "0" ? "😊" : "☹️");
    }).fail(function () {
        $("#result").text("Error");
    });
}

$(document).ready(function () {
    $("#submit").on("click", analyze);
});

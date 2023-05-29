from flask import Flask, render_template, request, jsonify
import os
import requests
from test_package_15551 import cookie2dict
from prometheus_client import Counter, Gauge, Histogram, Summary, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

MODEL_SERVICE_URL = os.environ.get("MODEL_HOST", "http://localhost:8081")
#MODEL_SERVICE_URL = "http://localhost:8081"

history = []

button_counter = Counter("button_counter", "Count the number of button presses.")
invalid_input_counter = Counter("invalid_input_counter", "Count the number of invalid user inputs.")
# time_individual = Gauge("gauge_time", "Count the duration for different steps.", ["step"])
# size_of_input = Histogram("histogram_size_of_input", "The number of characters in the input.", buckets=[0, 5, 10, 15, 20, 25, 50, 75, 100])
# time_summary = Summary("summary_time", "Summarizing duration for different steps", ["step"])

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

@app.route("/")
def home():
    return render_template('index.html', history=history)

@app.route("/analyze", methods=["POST"])
def analyze():
    global button_counter, invalid_input_counter

    button_counter.inc()
    
    review = request.form.get("review")
    restaurant = request.form.get('restaurant')

    # use the library to display information about the cookie
    print(cookie2dict('some cookie=true; some_other_cookie=false').ToDict())
    
    if not review:
        return jsonify({"error": "Review is empty."}), 400

    try:
        headers = {"accept": "application/json"}
        payload = {"text": review}
        response = requests.post(f"{MODEL_SERVICE_URL}/predict", json=payload, headers=headers)
        response.raise_for_status()
        sentiment = response.json()["sentiment"]
    except requests.exceptions.RequestException as e:
        invalid_input_counter.inc()
        return jsonify({"error": str(e)}), 500

    # record the review and its sentiment
    history.append({
        "review": review,
        "restaurant": restaurant,
        "sentiment": sentiment,
    })
    
    return jsonify({"sentiment": sentiment})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
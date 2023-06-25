from flask import Flask, render_template, request, jsonify, Response
import os
import requests
from test_package_15551 import cookie2dict
from prometheus_client import Counter, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)

MODEL_SERVICE_URL = os.environ.get("MODEL_HOST", "http://localhost:8081")
APP_VERSION = os.environ.get("APP_VERSION", "0.0.0.0")

history = []

button_counter = Counter("button_counter", "Count the number of button presses.")
invalid_input_counter = Counter("invalid_input_counter", "Count the number of invalid user inputs.")
correct_predictions = Counter("correct_predictions", "Count the number of correct predictions.")
wrong_predictions = Counter("wrong_predictions", "Count the number of wrong predictions.")

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

@app.route("/")
def home():
    app.logger.info("home page visited!")
    return render_template('index.html', history=history)

@app.route("/analyze", methods=["POST"])
def analyze():
    global button_counter, invalid_input_counter
    app.logger.info("review to analyze submitted...")
    button_counter.inc()
    
    review = request.form.get("review")
    restaurant = request.form.get('restaurant')

    # use the library to display information about the cookie
    print('APP_VERSION: ', APP_VERSION)
    print(cookie2dict('some cookie=true; some_other_cookie=false').ToDict())
    
    if not review:
        app.logger.error("review is empty!")
        return jsonify({"error": "Review is empty."}), 400

    try:
        headers = {"accept": "application/json"}
        payload = {"text": review}
        response = requests.post(f"{MODEL_SERVICE_URL}/predict", json=payload, headers=headers)
        response.raise_for_status()
        sentiment = response.json()["sentiment"]
        app.logger.info("response received from model service {}".format(sentiment))
    except requests.exceptions.RequestException as e:
        invalid_input_counter.inc()
        app.logger.warning("invalid input!")
        return jsonify({"error": str(e)}), 500

    # record the review and its sentiment
    history.append({
        "review": review,
        "restaurant": restaurant,
        "sentiment": sentiment,
    })
    
    return jsonify({"sentiment": sentiment})

@app.route("/evaluate/correct", methods=["POST"])
def correct():
    global correct_predictions
    correct_predictions.inc()
    app.logger.info("user feedback: correct prediction")
    return Response()

@app.route("/evaluate/wrong", methods=["POST"])
def wrong():
    global wrong_predictions
    wrong_predictions.inc()
    app.logger.info("user feedback: wrong prediction")
    return Response()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
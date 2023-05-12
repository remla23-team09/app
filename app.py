from flask import Flask, render_template, request, jsonify, Response
import os
import requests
from test_package_15551 import cookie2dict
from random import random

app = Flask(__name__)

MODEL_SERVICE_URL = os.environ.get("MODEL_HOST", "http://localhost:8081")

countHomePage = 0
countButtonPress = 0

@app.route("/")
def index():
    global countHomePage
    countHomePage += 1
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():

    global countButtonPress
    countButtonPress += 1
    
    review = request.form.get("review")
    print(cookie2dict('some cookie=true; some_other_cookie=false').ToDict())
    if not review:
        return jsonify({"error": "Review is empty."}), 400

    try:
        headers = {"accept": "application/json"}
        payload = {"text": review}
        response = requests.post(f"{MODEL_SERVICE_URL}/predict", json=payload, headers=headers)
        response.raise_for_status()
        prediction = response.json()["prediction"]
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"prediction": prediction})

@app.route('/metrics', methods=['GET'])
def metrics():
    global countHomePage, countButtonPress

    m = "# HELP my_random This is just a random 'gauge' for illustration.\n"
    m+= "# TYPE my_random gauge\n"
    m+= "my_random " + str(random()) + "\n\n"

    m+= "# HELP num_requests The number of requests that have been served, by page.\n"
    m+= "# TYPE num_requests counter\n"
    m+= "num_requests{{page=\"index\"}} {}\n".format(countHomePage)
    m+= "num_requests{{page=\"sub\"}} {}\n".format(countButtonPress)

    return Response(m, mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
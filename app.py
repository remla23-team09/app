from flask import Flask, render_template, request, jsonify, Response
import os
import requests
from test_package_15551 import cookie2dict
from random import random

app = Flask(__name__)

MODEL_SERVICE_URL = os.environ.get("MODEL_HOST", "http://localhost:8081")

count_home_page = 0
count_button_press = 0

@app.route("/")
def index():
    global count_home_page
    count_home_page += 1
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    # timer start
    global count_button_press
    count_button_press += 1
    
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
    # timeer end
    
    return jsonify({"prediction": prediction})

@app.route('/metrics', methods=['GET'])
def metrics():
    global count_home_page, count_button_press

    m = "# HELP my_random This is just a random 'gauge' for illustration.\n"
    m+= "# TYPE my_random gauge\n"
    m+= "my_random " + str(random()) + "\n\n"

    m+= "# HELP count_home_page The number of requests that have been served by page.\n"
    m+= "# TYPE count_home_page counter\n"
    m+= "count_home_page{{page=\"count_home_page\"}} {}\n".format(count_home_page)

    m+= "# HELP count_button_press The number of requests to the API.\n"
    m+= "# TYPE count_home_page counter\n"
    m+= "count_button_press{{page=\"count_button_press\"}} {}\n".format(count_button_press)

    return Response(m, mimetype="text/plain")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
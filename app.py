from flask import Flask, render_template, request, jsonify
import os
import requests
from test_package_15551 import cookie2dict

app = Flask(__name__)

MODEL_SERVICE_URL = os.environ.get("MODEL_HOST", "http://localhost:8081")

history = []

@app.route("/")
def home():
    return render_template('index.html', history=history)

@app.route("/analyze", methods=["POST"])
def analyze():
    
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
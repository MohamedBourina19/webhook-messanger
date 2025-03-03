import requests
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

ACCESS_TOKEN = "EAAQQA1jZB5X4BO2xMCZCOEMpjj8sZANib8YPx1hGBp8EVRAATtLCbV041Wke1Y3K0fEF6n0h3ZBEkGm7wwoENo51XZB1UipOVcn2mWDNjSfbsj2q7f7gKTZA27RyWpz6yLjnRWM6PxwiDrD8qDXbQu72UZCDoMJS9ZCSGEyZBIZASxP2ZBweZCKNxxPAdqqCiwLrsKIpRAZDZD"

@app.route("/", methods=["GET", "POST"])
def index():
    return jsonify({"message": "API is working!"}), 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        challenge = request.args.get("hub.challenge")
        verify_token = request.args.get("hub.verify_token")
        if mode == "subscribe" and verify_token:
            return challenge
        else:
            return jsonify({"message": "Invalid verify token"}), 401
    elif request.method == "POST":
        body = request.get_json()
        if body["object"] == "page":
            id = body["entry"][0]["messaging"][0]["sender"]["id"]
            msg = body["entry"][0]["messaging"][0]["message"]["text"]
            send_message(id, msg)
            return jsonify({"message": "Message received!"}), 200

def send_message(sender, message):
    api = "https://graph.facebook.com/v21.0/me/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "message": {"text": message},
        "recipient": {"id": sender}
    }
    requests.post(api, data=json.dumps(payload), headers=headers)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

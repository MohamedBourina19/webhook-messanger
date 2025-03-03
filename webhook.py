import requests
import json
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

ACCESS_TOKEN = "EAAQQA1jZB5X4BO2xMCZCOEMpjj8sZANib8YPx1hGBp8EVRAATtLCbV041Wke1Y3K0fEF6n0h3ZBEkGm7wwoENo51XZB1UipOVcn2mWDNjSfbsj2q7f7gKTZA27RyWpz6yLjnRWM6PxwiDrD8qDXbQu72UZCDoMJS9ZCSGEyZBIZASxP2ZBweZCKNxxPAdqqCiwLrsKIpRAZDZD"
DOMAIN = os.getenv("DOMAIN", "https://bogrinaxp.onrender.com")

user_data = {}

@app.route("/", methods=["GET"])
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
            entry = body["entry"][0]
            messaging_event = entry["messaging"][0]
            sender_id = messaging_event["sender"]["id"]
            if "message" in messaging_event:
                message_text = messaging_event["message"]["text"]
                if message_text.startswith("LINK@"):
                    name = message_text.split("@")[1]
                    user_data[sender_id] = name
                    link = f"{DOMAIN}/{name}"
                    send_message(sender_id, f"تم إنشاء الرابط: {link}")
            return jsonify({"message": "Message received!"}), 200

@app.route("/<name>", methods=["GET"])
def dynamic_link(name):
    for user_id, user_name in user_data.items():
        if user_name == name:
            ip = request.remote_addr
            user_agent = request.headers.get("User-Agent")
            device_info = f"تم فتح الرابط من:\nIP: {ip}\nDevice: {user_agent}"
            send_message(user_id, device_info)
            return f"Hello, {name}!", 200
    return "Name not found!", 404

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

import requests
import json
from flask import Flask, request
import time

app = Flask(__name__)

ACCESS_TOKEN = "EAAQQA1jZB5X4BO2xMCZCOEMpjj8sZANib8YPx1hGBp8EVRAATtLCbV041Wke1Y3K0fEF6n0h3ZBEkGm7wwoENo51XZB1UipOVcn2mWDNjSfbsj2q7f7gKTZA27RyWpz6yLjnRWM6PxwiDrD8qDXbQu72UZCDoMJS9ZCSGEyZBIZASxP2ZBweZCKNxxPAdqqCiwLrsKIpRAZDZD"
DEEPSEEK_KEY = "sk-fcb45cbd6f5f4f67b9bfb954c19b36ee"

def mark_message_as_seen(sender_id):
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": sender_id},
        "sender_action": "mark_seen"
    }
    requests.post(url, headers=headers, data=json.dumps(data))

def send_typing_indicator(sender_id):
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": sender_id},
        "sender_action": "typing_on"
    }
    requests.post(url, headers=headers, data=json.dumps(data))

def send_message(sender_id, message):
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": sender_id},
        "message": {"text": message}
    }
    requests.post(url, headers=headers, data=json.dumps(data))

def send_like_reaction(sender_id, message_id):
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": sender_id},
        "sender_action": "react",
        "reaction": {"reaction": "♥", "mid": message_id}
    }
    requests.post(url, headers=headers, data=json.dumps(data))

def deepseek_image_recognition(image_url):
    headers = {"Authorization": f"Bearer {DEEPSEEK_KEY}"}
    response = requests.post("https://api.deepseek.com/v1/vision", headers=headers, json={"url": image_url})
    return response.json()

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        return request.args.get("hub.challenge"), 200
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def handle_messages():
    data = request.get_json()
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                sender_id = messaging_event["sender"]["id"]
                mark_message_as_seen(sender_id)  # Mark the message as seen
                if "message" in messaging_event:
                    message_id = messaging_event["message"]["mid"]  # Get the message ID
                    send_like_reaction(sender_id, message_id)  # Send a like reaction (♥)
                    if "text" in messaging_event["message"]:
                        message_text = messaging_event["message"]["text"]
                        send_typing_indicator(sender_id)  # Show typing indicator
                        time.sleep(2)  # Simulate typing delay
                        send_message(sender_id, f"لقد قلت: {message_text}")
                    elif "attachments" in messaging_event["message"]:
                        for attachment in messaging_event["message"]["attachments"]:
                            if attachment["type"] == "image":
                                image_url = attachment["payload"]["url"]
                                send_typing_indicator(sender_id)  # Show typing indicator
                                time.sleep(2)  # Simulate typing delay
                                recognition_result = deepseek_image_recognition(image_url)
                                send_message(sender_id, f"نتيجة التعرف على الصورة: {recognition_result}")
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

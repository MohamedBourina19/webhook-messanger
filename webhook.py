import requests
import json
from flask import Flask, request
import time

app = Flask(__name__)

ACCESS_TOKEN = "EAAQQA1jZB5X4BO2xMCZCOEMpjj8sZANib8YPx1hGBp8EVRAATtLCbV041Wke1Y3K0fEF6n0h3ZBEkGm7wwoENo51XZB1UipOVcn2mWDNjSfbsj2q7f7gKTZA27RyWpz6yLjnRWM6PxwiDrD8qDXbQu72UZCDoMJS9ZCSGEyZBIZASxP2ZBweZCKNxxPAdqqCiwLrsKIpRAZDZD"
OPENROUTER_API_KEY = "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"

def mark_message_as_seen(sender_id):
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    data = {"recipient": {"id": sender_id}, "sender_action": "mark_seen"}
    requests.post(url, headers=headers, data=json.dumps(data))

def send_typing_indicator(sender_id):
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    data = {"recipient": {"id": sender_id}, "sender_action": "typing_on"}
    requests.post(url, headers=headers, data=json.dumps(data))

def send_message(sender_id, message):
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    data = {"recipient": {"id": sender_id}, "message": {"text": message}}
    requests.post(url, headers=headers, data=json.dumps(data))

def get_ai_response(user_message):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
        data=json.dumps({
            "model": "deepseek/deepseek-r1:free",
            "messages": [{"role": "user", "content": user_message}],
            "temperature": 0.85,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "repetition_penalty": 1,
            "top_k": 0
        })
    )
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    return None

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        return request.args.get("hub.challenge"), 200
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def handle_messages():
    data = request.get_json()
    if data["object"] != "page":
        return "ok", 200

    entry = data["entry"][0] if data["entry"] else None
    if not entry:
        return "ok", 200

    messaging_event = entry["messaging"][0] if entry["messaging"] else None
    if not messaging_event or "message" not in messaging_event:
        return "ok", 200

    sender_id = messaging_event["sender"]["id"]
    mark_message_as_seen(sender_id)
    send_typing_indicator(sender_id)

    if "text" in messaging_event["message"]:
        message_text = messaging_event["message"]["text"]
        time.sleep(2)
        ai_response = get_ai_response(message_text)
        if ai_response:
            send_message(sender_id, ai_response)

    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

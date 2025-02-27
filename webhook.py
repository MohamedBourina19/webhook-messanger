import requests
import json
from flask import Flask, request
import time

app = Flask(__name__)

ACCESS_TOKEN = "EAAQQA1jZB5X4BO2xMCZCOEMpjj8sZANib8YPx1hGBp8EVRAATtLCbV041Wke1Y3K0fEF6n0h3ZBEkGm7wwoENo51XZB1UipOVcn2mWDNjSfbsj2q7f7gKTZA27RyWpz6yLjnRWM6PxwiDrD8qDXbQu72UZCDoMJS9ZCSGEyZBIZASxP2ZBweZCKNxxPAdqqCiwLrsKIpRAZDZD"
OPENROUTER_API_KEY = "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"

def send_message(sender_id, text):
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={ACCESS_TOKEN}"
    data = {"recipient": {"id": sender_id}, "message": {"text": text}}
    requests.post(url, json=data)

def get_ai_response(text):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}"},
        json={"model": "deepseek/deepseek-r1:free", "messages": [{"role": "user", "content": text}]}
    )
    return response.json()["choices"][0]["message"]["content"]

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        return request.args.get("hub.challenge"), 200
    return "Error", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data["object"] == "page":
        message = data["entry"][0]["messaging"][0]["message"]
        sender_id = data["entry"][0]["messaging"][0]["sender"]["id"]
        response = get_ai_response(message["text"])
        send_message(sender_id, response)
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

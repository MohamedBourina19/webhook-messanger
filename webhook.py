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

def send_like_reaction(sender_id, message_id):
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    data = {"recipient": {"id": sender_id}, "sender_action": "react", "reaction": {"reaction": "♥", "mid": message_id}}
    requests.post(url, headers=headers, data=json.dumps(data))

def get_ai_response(user_message):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"},
        data=json.dumps({"model": "deepseek/deepseek-r1-distill-llama-8b", "messages": [{"role": "user", "content": user_message}]})
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
    if data["object"] == "page":
        id = data["entry"][0]["messaging"][0]["sender"]["id"]
        send_like_reaction(id)
        send_typing_indicator(id)
        mark_message_as_seen(id)
        msg = data["entry"][0]["messaging"][0]["message"]["text"]
        response = requests.post(url="https://openrouter.ai/api/v1/chat/completions",
        headers={
           "Authorization": "Bearer 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",
           "Content-Type": "application/json",  },
        data=json.dumps({"model": "deepseek/deepseek-r1-distill-llama-8b","messages": [{"role": "user","content": msg}],}))
        res = response.json()["choices"][0]["message"]["content"]
        url = "https://graph.facebook.com/v21.0/me/messages"
        header = {"Authorization": "Bearer EAAQQA1jZB5X4BO9gulIGruLuSNQZBK4nLBecjEmZBprer0huHjHEb9RHg6GJh686AwcSZAe4LwlT34Qxbpyj6XZBpWSRN3ZB1jcqJ12ZCGZBHdnvifiZBSyCEjbaqRjZBFtjts9iAFIjdHPMQ0ZBhZA62IdYnaXHyCwy1iTsY8yUiAesRwJiRZAV7GVixPvdPCgNb2J5x4gZDZD"}
        payload = {"message": {"text": res},"recipient": {"id": "9089172697785732"}}
        requests.post(url, json=payload,headers=header)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

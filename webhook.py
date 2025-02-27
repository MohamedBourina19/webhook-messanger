from flask import Flask, request, jsonify
import requests
import time
import threading

app = Flask(__name__)

# Replace with your Facebook Page Access Token
PAGE_ACCESS_TOKEN = "EAAQQA1jZB5X4BO2xMCZCOEMpjj8sZANib8YPx1hGBp8EVRAATtLCbV041Wke1Y3K0fEF6n0h3ZBEkGm7wwoENo51XZB1UipOVcn2mWDNjSfbsj2q7f7gKTZA27RyWpz6yLjnRWM6PxwiDrD8qDXbQu72UZCDoMJS9ZCSGEyZBIZASxP2ZBweZCKNxxPAdqqCiwLrsKIpRAZDZD"
QURAN_API_URL = "http://api.alquran.cloud/v1/juz/{}"  # Quran API

# Function to send a message
def send_message(recipient_id, text):
    url = "https://graph.facebook.com/v21./me/messages"
    headers = {
        "Authorization": f"Bearer {PAGE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

# Function to mark messages as read
def mark_message_as_read(recipient_id):
    url = "https://graph.facebook.com/v21.0/me/messages"
    headers = {
        "Authorization": f"Bearer {PAGE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "recipient": {"id": recipient_id},
        "sender_action": "mark_seen"
    }
    requests.post(url, headers=headers, json=payload)

# Function to show typing indicator
def show_typing_indicator(recipient_id):
    url = "https://graph.facebook.com/v21.0/me/messages"
    headers = {
        "Authorization": f"Bearer {PAGE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "recipient": {"id": recipient_id},
        "sender_action": "typing_on"
    }
    requests.post(url, headers=headers, json=payload)

# Function to hide typing indicator
def hide_typing_indicator(recipient_id):
    url = "https://graph.facebook.com/v21.0/me/messages"
    headers = {
        "Authorization": f"Bearer {PAGE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "recipient": {"id": recipient_id},
        "sender_action": "typing_off"
    }
    requests.post(url, headers=headers, json=payload)

# Function to set the bot as online
def set_bot_online():
    url = "https://graph.facebook.com/v21.0/me/messenger_profile"
    headers = {
        "Authorization": f"Bearer {PAGE_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "get_started": {"payload": "GET_STARTED"},
        "greeting": [
            {
                "locale": "default",
                "text": "مرحبًا! أنا بوت القرآن الكريم. أرسل لي رسالة وسأرد عليك."
            }
        ]
    }
    requests.post(url, headers=headers, json=payload)

# Function to get Quran Juz
def get_quran_juz(juz_number):
    response = requests.get(QURAN_API_URL.format(juz_number))
    if response.status_code == 200:
        data = response.json()
        return data["data"]["ayahs"]
    return None

# Function to post Quran Juz every 10 minutes
def post_quran_juz():
    juz_number = 1
    while True:
        ayahs = get_quran_juz(juz_number)
        if ayahs:
            text = "\n".join([f"{ayah['text']} ({ayah['surah']['name']} {ayah['numberInSurah']})" for ayah in ayahs])
            send_message("USER_ID", text)  # Replace USER_ID with the target user ID
        juz_number = (juz_number % 30) + 1  # Loop through Juz 1 to 30
        time.sleep(600)  # Wait for 10 minutes

# Webhook endpoint
@app.route("/webhook", methods=["POST"])
def POST_WEBHOOK():
    data = request.get_json()
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                sender_id = messaging_event["sender"]["id"]
                if "message" in messaging_event:
                    mark_message_as_read(sender_id)
                    show_typing_indicator(sender_id)
                    message_text = messaging_event["message"]["text"]
                    time.sleep(2)  # Simulate typing delay
                    hide_typing_indicator(sender_id)
                    send_message(sender_id, message_text)  # Echo the message
    return "EVENT_RECEIVED", 200

# Webhook verification endpoint
@app.route("/webhook", methods=["GET"])
def GET_WEBHOOK():
    verify_token = request.args.get("hub.verify_token")
    if verify_token:  # Replace with your verify token
        return request.args.get("hub.challenge")
    return "Invalid verification token", 403

# Start the Quran posting thread
def start_quran_thread():
    quran_thread = threading.Thread(target=post_quran_juz)
    quran_thread.daemon = True
    quran_thread.start()

if __name__ == "__main__":
    set_bot_online()  # Set bot as online
    start_quran_thread()  # Start Quran posting thread
    app.run(host="0.0.0.0", port=5000, debug=True)

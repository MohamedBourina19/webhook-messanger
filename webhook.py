import requests
from flask import Flask
from flask import request
from flask import jsonify

ACCESS_TOKEN = "EAAQQA1jZB5X4BO2xMCZCOEMpjj8sZANib8YPx1hGBp8EVRAATtLCbV041Wke1Y3K0fEF6n0h3ZBEkGm7wwoENo51XZB1UipOVcn2mWDNjSfbsj2q7f7gKTZA27RyWpz6yLjnRWM6PxwiDrD8qDXbQu72UZCDoMJS9ZCSGEyZBIZASxP2ZBweZCKNxxPAdqqCiwLrsKIpRAZDZD"

app = Flask(__name__)
@app.route("/", methods=["GET","POST"])
def index():
  return jsonify({"message":"error api"}),404
@app.route("/webhook", methods=["GET"])
def settings():
  if request.method == "GET":
    mode = request.args.get("hub.mode")
    challenge = request.args.get("hub.challenge")
    verify_token = request.args.get("hub.verify_token")
    if mode == "subscribe":
      return challenge
@app.route("/webhook", methods=["POST"])
def webhook():
  body = request.get_json()
  if body["object"] == "page":
    id = ["entry"][0]["messaging"][0]["sender"]["id"]
    msg = ["entry"][0]["messaging"][0]["message"]["text"] 
    url = f"https://graph.facebook.com/v12.0/me/messages?access_token={ACCESS_TOKEN}"
    headers = {"Content-Type": "application/json"}
    data = {"recipient": {"id": id}, "sender_action": "mark_seen"}
    requests.post(url, headers=headers, data=json.dumps(data))
    data = {"recipient": {"id":id}, "sender_action": "typing_on"}
    requests.post(url, headers=headers, data=json.dumps(data))
    headers = {"Content-Type": "application/json"}
    data = {"recipient": {"id":id}, "message": {"text": msg}}
    requests.post(url, headers=headers, data=json.dumps(data))

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)







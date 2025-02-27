from flask import Flask
from flask import request 
from flask import jsonify
import requests

app = Flask(__name__)

url = "https://graph.facebook.com/v21.0/me/messages"
VERIFY_TOKEN = "chatbot"

@app.route("/", methods=["GET","POST"])
def index():
  return jsonify({"message":"error api"}),404
@app.route("/webhook", methods=["GET"])
def GET_WEBHOOK():
  mode = request.args.get("hub.mode")
  token = request.args.get("hub.verify_token")
  challenge = request.args.get("hub.challenge")
  if mode == "subscribe" and token == "chatbot":
    return challenge
  else:
    return jsonify({"message":"error args"})
@app.route("/webhook", methods=["POST"])
def POST_WEBHOOK():
  data = request.get_json()
  if data["object"] == "page":
    id = data["entry"][0]["messaging"][0]["sender"]["id"]
    msg = data["entry"][0]["messaging"][0]["message"]["text"]
    header = {"Authorization": "Bearer EAAQQA1jZB5X4BO2xMCZCOEMpjj8sZANib8YPx1hGBp8EVRAATtLCbV041Wke1Y3K0fEF6n0h3ZBEkGm7wwoENo51XZB1UipOVcn2mWDNjSfbsj2q7f7gKTZA27RyWpz6yLjnRWM6PxwiDrD8qDXbQu72UZCDoMJS9ZCSGEyZBIZASxP2ZBweZCKNxxPAdqqCiwLrsKIpRAZDZD"}
    payload = {"message": {"text": msg},"recipient": {"id": f"{id}"}}
    requests.post(url, json=payload,headers=header)
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)
 





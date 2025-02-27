from flask import Flask
from flask import request
from flask import jsonify
import requests 
import json
VERIFY_TOKEN = "mohamedbougrina19"

app = Flask(__name__)
@app.route("/", methods=["GET","POST"])
def message():return jsonify({"message":"error api"})
@app.route("/webhook", methods=["GET","POST"])
def webhook():
   if request.method == "GET":
      model = request.args.get("hub.model")
      token = request.args.get("hub.verify_token")
      challenge = request.args.get("hub.challenge")
      if model == "subscribe" and token == VERIFY_TOKEN:
         return jsonify({"message": challenge})
      else:return jsonify({"message":"error data request"})
   if request.method == "POST":
      data =  request.get_json()
      if data["object"] == "page":
         id = data["entry"][0]["messaging"][0]["sender"]["id"]
         msg = data["entry"][0]["messaging"][0]["message"]["text"]
         url = "https://graph.facebook.com/v21.0/me/messages"
         header = {"Authorization": "Bearer EAAQQA1jZB5X4BO9gulIGruLuSNQZBK4nLBecjEmZBprer0huHjHEb9RHg6GJh686AwcSZAe4LwlT34Qxbpyj6XZBpWSRN3ZB1jcqJ12ZCGZBHdnvifiZBSyCEjbaqRjZBFtjts9iAFIjdHPMQ0ZBhZA62IdYnaXHyCwy1iTsY8yUiAesRwJiRZAV7GVixPvdPCgNb2J5x4gZDZD"}
         payload = {"message": {"text": msg},"recipient": {"id": id}}
         requests.post(url, json=payload,headers=header)
       
if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5000, debug=True) 

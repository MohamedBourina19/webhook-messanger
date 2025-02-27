from flask import Flask
from flask import request
import json

def json_save(debug, key):
  index = {}
  try:
      try:
        with open("debug.json", "r") as debugs:
           index = json.load(debugs)
      except(FileNotFoundError, json.JSONDecodeError) as error :
           return str(error)
      if "debug" not in index:
         index["debug"]={key:[]}
      index["debug"][key].append(debug)
      with open("debug.json", "w") as file_debugs:
         json.dump(index, file_debugs, indent=2)
  except Exception as error :
       return str(error) 
app = Flask(__name__)
@app.route("/", methods=["GET","POST"])
def dashboard():return "error api :-)"
@app.route("/webhook", methods=["GET","POST"])
def requesting():
   if request.method == "GET":
      mode = request.args.get("hub.mode")
      json_save(mode, "hub")
      token = request.args.get("hub.verify_token")
      json_save(token, "hub")
      challenge = request.args.get("hub.challenge")
      json_save(challenge, "hub")
      return challenge
   if request.method == "POST":
      data = request.get_json()
      json_save(data, "data_json")
@app.route("/your/data/", methods=["GET","POST"])
def show():
   with open("debug.json", "r") as debugs:
      return json.load(debugs)
if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5000, debug=True)      

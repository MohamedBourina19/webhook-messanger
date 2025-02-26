from flask import Flask, request, jsonify
import sqlite3
import json
import requests

app = Flask(__name__)

conn = sqlite3.connect('facebook.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
''')

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if mode == 'subscribe':
            return challenge
        else:
            return 'Invalid verify token', 403

    elif request.method == 'POST':
        data = request.get_json()
        if data['object'] == 'page':
            for entry in data['entry']:
                for messaging in entry['messaging']:
                    if messaging['message']:
                        sender_id = messaging['sender']['id']
                        message = messaging['message']['text']
                        timestamp = messaging['timestamp']
                        cursor.execute('INSERT INTO messages (sender_id, message, timestamp) VALUES (?, ?, ?)', (sender_id, message, timestamp))
                        conn.commit()
                        send_message(sender_id, message)
        return 'OK', 200

def send_message(sender_id, message):
    url = 'https://graph.facebook.com/v13.0/me/messages'
    token = 'EAAO52Vx4rI0BOzZBgcdG9hqUkYCdIOU2y2OJlg5ab7lv9z4e38iZCB41r4ZB5zZCFwrj8hkfJ7ZCrEsuOu1i2yXQQ13h6uXncU6E4VhI7n1noVAwF1qcoOmcAkDcyN2FcgZAE3ZAMOu4f9ZCOs7rxzQkd3uZC0srFJBY6amZB3IgQsgKNWmx1CbASdZB1vZAk8sNNsopggZDZD'
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'recipient': {
            'id': sender_id
        },
        'message': {
            'text': message
        }
    }
    response = requests.post(url, headers=headers, json=data, params={'access_token': token})
    if response.status_code != 200:
        print('Error sending message:', response.text)

@app.route('/messages', methods=['GET'])
def get_messages():
    cursor.execute('SELECT * FROM messages')
    messages = cursor.fetchall()
    return jsonify({'messages': messages})

if __name__ == '__main__':
    app.run()

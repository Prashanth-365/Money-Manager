from flask import Flask, request
import requests

TOKEN = "7903944339:AAGFxbIv4MA0qhht7qX5rACzPTpfTCYNYl8"
app = Flask(__name__)


@app.route("/telegram_webhook", methods=["POST"])
def receive_update():
    data = request.json
    print(data)  # Print entire update for debugging

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        print(f"Chat ID: {chat_id}")

        # Send a reply (optional)
        send_message(chat_id, f"Your Chat ID is: {chat_id}")

    return "OK"

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

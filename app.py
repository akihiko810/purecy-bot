from flask import Flask, request
import openai
import os
import requests

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()

        events = data.get("events", [])
        if not events:
            return "No events", 200

        event = events[0]
        user_message = event.get("message", {}).get("text")
        reply_token = event.get("replyToken")

        if not user_message or not reply_token:
            return "Missing message or token", 200

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply_text = response.choices[0].message.content

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
        }
        body = {
            "replyToken": reply_token,
            "messages": [{"type": "text", "text": reply_text}]
        }

        requests.post(
            "https://api.line.me/v2/bot/message/reply",
            headers=headers,
            json=body
        )

        return "OK", 200

    except Exception as e:
        print(f"Error: {e}")
        return "Internal Server Error", 500

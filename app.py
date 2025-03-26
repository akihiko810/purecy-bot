from flask import Flask, request
import openai
import os
import requests
import threading

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

def reply_to_line(reply_token, reply_text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": reply_text}]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)

def handle_message(user_message, reply_token):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply_text = response.choices[0].message.content
    except Exception as e:
        print("OpenAI Error:", e)
        reply_text = "申し訳ありません、ただいまアクセスが集中しています。時間をおいて再度お試しください。"

    reply_to_line(reply_token, reply_text)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        events = data.get("events", [])
        if len(events) == 0 or events[0].get("type") != "message":
            return "OK"

        user_message = events[0]["message"]["text"]
        reply_token = events[0]["replyToken"]

        threading.Thread(target=handle_message, args=(user_message, reply_token)).start()

    except Exception as e:
        print("Webhook Error:", e)
    
    return "OK"

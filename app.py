from flask import Flask, request
import openai
import os
import requests
import threading

app = Flask(__name__)

openai_api_key = os.getenv("OPENAI_API_KEY")
line_channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# 最新のOpenAI API形式を使ったメッセージ送信関数
def handle_message(user_message, reply_token):
    from openai import OpenAI
    client = OpenAI(api_key=openai_api_key)

    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": user_message}
        ]
    )
    reply_text = chat_completion.choices[0].message.content

    reply_to_line(reply_text, reply_token)

def reply_to_line(reply_text, reply_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {line_channel_access_token}"
    }
    body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": reply_text}]
    }
    requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        events = data.get("events", [])
        
        for event in events:
            if event.get("type") == "message" and "text" in event["message"]:
                user_message = event["message"]["text"]
                reply_token = event["replyToken"]

                # 別スレッドでOpenAI処理を実行
                threading.Thread(
                    target=handle_message,
                    args=(user_message, reply_token)
                ).start()
        return "OK"
    except Exception as e:
        print(f"Webhook error: {e}")
        return "Internal Server Error", 500

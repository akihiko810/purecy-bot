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
    print("🛠 handle_message() 発火しました！")
    from openai import OpenAI
    client = OpenAI(api_key=openai_api_key)

    chat_completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    reply_text = chat_completion.choices[0].message.content
    print("💬 OpenAIの応答:", reply_text)

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
        print("✅ 受信データ:", data)  # ← この行を追加
        events = data.get("events", [])

        for event in events:
            if event.get("type") == "message" and event["message"].get("type") == "text":
                user_message = event["message"]["text"]
                reply_token = event["replyToken"]
                print("🟢 ユーザーからのメッセージ:", user_message)  # ← 追加
                print("🔁 reply_token:", reply_token)  # ← 追加

                threading.Thread(
                    target=handle_message,
                    args=(user_message, reply_token)
                ).start()

        return "OK"
    except Exception as e:
        print(f"❌ Error: {e}")
        return "Internal Server Error", 500

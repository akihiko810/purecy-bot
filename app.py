from flask import Flask, request
import os
import openai
import requests

app = Flask(__name__)

# 環境変数からAPIキー取得
openai_api_key = os.getenv("OPENAI_API_KEY")
line_channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

# OpenAIクライアント初期化
client = openai.OpenAI(api_key=openai_api_key)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        user_message = data["events"][0]["message"]["text"]
        reply_token = data["events"][0]["replyToken"]

        # OpenAI GPTで応答を生成
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_message}]
        )
        reply_text = chat_completion.choices[0].message.content

        # LINEメッセージ返信API
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {line_channel_access_token}"
        }
        body = {
            "replyToken": reply_token,
            "messages": [{
                "type": "text",
                "text": reply_text
            }]
        }
        requests.post("https://api.line.me/v2/bot/message/reply", headers=headers, json=body)

        return "OK"
    
    except Exception as e:
        print(f"Error: {e}")
        return "Internal Server Error", 500

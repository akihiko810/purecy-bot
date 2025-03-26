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
        user_message = data["events"][0]["message"]["text"]
        reply_token = data["events"][0]["replyToken"]

        # ✅ 新しい OpenAI 形式（v1.0.0 以降）
        client = openai.OpenAI(api_key=openai.api_key)
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        reply_text = chat_completion.choices[0].message.content

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
        return "OK"

    except Exception as e:
        print(f"Error: {e}")
        return "Internal Server Error", 500

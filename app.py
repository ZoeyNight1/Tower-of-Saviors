from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from database import set_max_stamina, get_max_stamina
from utils import calculate_full_time
import os

app = Flask(__name__)

# 用環境變數管理金鑰（Render 支援）
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()

    if text.startswith("上限"):
        try:
            max_stamina = int(text.replace("上限", "").strip())
            set_max_stamina(user_id, max_stamina)
            reply = f"已設定體力上限為 {max_stamina}"
        except:
            reply = "請輸入正確格式，例如：上限 150"

    elif text.startswith("目前"):
        try:
            current = int(text.replace("目前", "").strip())
            max_stamina = get_max_stamina(user_id)
            if not max_stamina:
                reply = "請先輸入上限，例如：上限 150"
            else:
                missing, full_time = calculate_full_time(max_stamina, current)
                reply = f"你還缺 {missing} 體力，預計在 {full_time.strftime('%Y/%m/%d %H:%M')} 回滿！"
        except:
            reply = "請輸入正確格式，例如：目前 123"
    else:
        reply = "請輸入「上限 150」或「目前 123」來使用體力計算功能。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    app.run()

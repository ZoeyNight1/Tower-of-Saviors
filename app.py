from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from database import set_max_stamina, get_max_stamina
from utils import calculate_full_time
from datetime import datetime
import os

app = Flask(__name__)

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

    max_stamina = None
    current_stamina = None

    if "上限" in text and "目前" in text:
        try:
            max_part = text.split("上限")[1].split("目前")[0].strip()
            cur_part = text.split("目前")[1].strip()
            max_stamina = int(max_part)
            current_stamina = int(cur_part)
            set_max_stamina(user_id, max_stamina)
            missing, full_time = calculate_full_time(max_stamina, current_stamina)
            reply = (
                f"已設定體力上限為 {max_stamina}，目前體力 {current_stamina}\n"
                f"你還缺 {missing} 體力，預計在 {full_time.strftime('%Y/%m/%d %H:%M')} 回滿"
            )
        except:
            reply = "請輸入正確格式，例如：上限150 目前123"

    elif text.startswith("上限"):
        try:
            max_stamina = int(text.replace("上限", "").strip())
            set_max_stamina(user_id, max_stamina)
            reply = f"已設定體力上限為 {max_stamina}"
        except:
            reply = "請輸入正確格式，例如：上限150"

    elif text.startswith("目前"):
        try:
            current_stamina = int(text.replace("目前", "").strip())
            max_stamina = get_max_stamina(user_id)
            if not max_stamina:
                reply = "請先輸入上限，例如：上限150"
            else:
                missing, full_time = calculate_full_time(max_stamina, current_stamina)
                reply = f"你還缺 {missing} 體力，預計在 {full_time.strftime('%Y/%m/%d %H:%M')} 回滿"
        except:
            reply = "請輸入正確格式，例如：目前123"
    elif text.startswith("目前") and len(text.split()) == 2:
        try:
            part = text.split()
            current = int(part[0].replace("目前", "").strip())
            target_time = datetime.strptime(part[1], "%Y/%m/%d %H:%M")

            now = datetime.now()
            delta = (target_time - now).total_seconds()
            if delta < 0:
                reply = "你輸入的時間已經過去了喔"
            else:
                recovered = int(delta // 480)  # 8分鐘回1點體
                estimated = current + recovered
                reply = f"預計到 {part[1]} 你會回到 {estimated} 體力"
        except Exception as e:
            reply = "請輸入正確格式，例如：目前123 2025/04/13 08:30"


    else:
        reply = "請輸入「上限150 目前123」或「上限150」、「目前123」來使用體力計算功能。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    app.run()

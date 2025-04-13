from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from database import set_max_stamina, get_max_stamina
from utils import calculate_full_time
import os
from datetime import datetime

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

    reply = "請輸入「上限 150」或「目前 123」來使用體力計算功能。"

    if "上限" in text and "目前" in text:
        try:
            parts = text.replace("上限", "").replace("目前", " ").split()
            max_stamina = int(parts[0])
            current = int(parts[1])
            set_max_stamina(user_id, max_stamina)
            missing, full_time = calculate_full_time(max_stamina, current)
            reply = f"已設定體力上限為 {max_stamina}\n你還缺 {missing} 體力，預計在 {full_time.strftime('%Y/%m/%d %H:%M')} 回滿！"
        except:
            reply = "請輸入正確格式，例如：上限150 目前123"

    elif text.startswith("目前") and "時間" in text:
        try:
            current_part, time_part = text.split("時間")
            current = int(current_part.replace("目前", "").strip())
            time_str = time_part.strip()

            if len(time_str.split(" ")[0].split("/")) == 2:
                year = datetime.now().year
                time_str = f"{year}/{time_str}"

            target_time = datetime.strptime(time_str, "%Y/%m/%d %H:%M")
            now = datetime.now()
            delta = (target_time - now).total_seconds()

            if delta < 0:
                reply = "你輸入的時間已經過去了喔"
            else:
                recovered = int(delta // 480)
                estimated = current + recovered
                reply = f"預計到 {target_time.strftime('%Y/%m/%d %H:%M')} 你會回到 {estimated} 體力"
        except Exception as e:
            reply = "請輸入正確格式，例如：目前123 時間04/13 08:30"

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
            reply = "請輸入正確格式，例如：目前123"

    elif text.startswith("上限"):
        try:
            max_stamina = int(text.replace("上限", "").strip())
            set_max_stamina(user_id, max_stamina)
            reply = f"已設定體力上限為 {max_stamina}"
        except:
            reply = "請輸入正確格式，例如：上限 150"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    app.run()

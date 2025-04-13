import re
from datetime import datetime

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
        parts = text.split()
        if len(parts) == 3:
            try:
                current = int(parts[1])
                time_str = parts[2]

                if len(time_str) == 16:
                    target_time = datetime.strptime(time_str, "%Y/%m/%d %H:%M")
                elif len(time_str) == 11:
                    year = datetime.now().year
                    target_time = datetime.strptime(f"{year}/{time_str}", "%Y/%m/%d %H:%M")
                else:
                    raise ValueError("時間格式錯誤")

                now = datetime.now()
                minutes_diff = int((target_time - now).total_seconds() / 60)
                recovered = max(0, minutes_diff // 8)

                max_stamina = get_max_stamina(user_id)
                if not max_stamina:
                    reply = "請先輸入上限，例如：上限 150"
                else:
                    new_stamina = current + recovered
                    reply = (
                        f"從現在起到 {target_time.strftime('%Y/%m/%d %H:%M')}，"
                        f"預計恢復 {recovered} 點體力，"
                        f"總體力為 {min(new_stamina, max_stamina)}（但最多為 {max_stamina}）"
                    )
            except:
                reply = "請確認格式與日期時間正確，例如：目前 123 2025/04/15 08:30"
        elif len(parts) == 2:
            try:
                current = int(parts[1])
                max_stamina = get_max_stamina(user_id)
                if not max_stamina:
                    reply = "請先輸入上限，例如：上限 150"
                else:
                    missing, full_time = calculate_full_time(max_stamina, current)
                    reply = f"你還缺 {missing} 體力，預計在 {full_time.strftime('%Y/%m/%d %H:%M')} 回滿"
            except:
                reply = "請輸入正確格式，例如：目前 123"
        else:
            reply = (
                "請輸入正確格式，例如：\n"
                "目前 123\n"
                "或 目前 123 2025/04/15 08:30"
            )


    elif text.startswith("目前"):
        try:
            current = int(text.replace("目前", "").strip())
            max_stamina = get_max_stamina(user_id)
            if not max_stamina:
                reply = "請先輸入上限，例如：上限 150"
            else:
                missing, full_time = calculate_full_time(max_stamina, current)
                reply = f"你還缺 {missing} 體力，預計在 {full_time.strftime('%Y/%m/%d %H:%M')} 回滿"
        except:
            reply = "請輸入正確格式，例如：目前 123"

    else:
        reply = (
            "請輸入：\n"
            "「上限 150」設定體力上限\n"
            "「目前 123」查詢回滿時間\n"
            "「目前 123 到 2025/04/15 08:30」查指定時間體力"
        )

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

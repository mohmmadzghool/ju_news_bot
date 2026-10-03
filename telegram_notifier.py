import os
import requests

# نقرأ التوكن والشات آي دي من متغيرات البيئة (أكثر أماناً وحماية)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(source, title, link):
    """
    إرسال إشعار بتنسيق جميل إلى تلجرام
    """
    if not BOT_TOKEN or not CHAT_ID:
        print("خطأ: مفاتيح التلجرام غير متوفرة!")
        return False

    message_text = (
        f"📢 *إعلان جديد من {source}*\n\n"
        f"📌 *العنوان:* {title}\n\n"
        f"🔗 [اضغط هنا لفتح الإعلان]({link})"
    )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message_text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            return True
        else:
            print(f"فشل الإرسال: {response.text}")
            return False
    except Exception as e:
        print(f"حدث خطأ أثناء الاتصال بتلجرام: {e}")
        return False
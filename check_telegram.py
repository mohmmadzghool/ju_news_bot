import os
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

CHANNELS = [
    {
        "name": "قناة الجامعة الأردنية الرسمية",
        "username": "universityofjordanofficial"
    },
    {
        "name": "أخبار الجامعة الأردنية",
        "username": "JUposts"
    }
]

HISTORY_FILE = "sent_tg_posts.txt"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_to_history(post_id):
    with open(HISTORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"{post_id}\n")

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload)

def check_telegram_channels():
    seen_posts = load_history()

    for ch in CHANNELS:
        url = f"https://t.me/s/{ch['username']}"
        try:
            res = requests.get(url, timeout=15)
            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.text, "html.parser")
            messages = soup.find_all("div", class_="tgme_widget_message")

            for msg in messages[-3:]:
                data_post = msg.get("data-post")
                if not data_post or data_post in seen_posts:
                    continue

                text_div = msg.find("div", class_="tgme_widget_message_text")
                post_text = text_div.get_text(separator="\n").strip() if text_div else ""

                if not post_text:
                    continue

                message_body = (
                    f"📢 <b>منشور جديد من {ch['name']}</b>\n\n"
                    f"{post_text}\n\n"
                    f"🔗 <a href='https://t.me/{data_post}'>رابط المنشور الأصلي</a>"
                )

                send_telegram(message_body)
                save_to_history(data_post)
                seen_posts.add(data_post)

        except Exception as e:
            print(f"Error checking {ch['username']}: {e}")

if __name__ == "__main__":
    check_telegram_channels()

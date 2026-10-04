import os
import json
import requests
from sites.site_ju_official import fetch_ju_official_news
from sites.site_ju_reg_bachelor import fetch_ju_reg_bachelor_news
from sites.site_ju_reg_grad import fetch_ju_reg_grad_news
from sites.site_ju_student_affairs import fetch_ju_student_affairs_news
from sites.site_ju_community_service import fetch_ju_community_service_news
from sites.site_ju_finance import fetch_ju_finance_news
from sites.site_ju_language_center import fetch_ju_language_center_news
from sites.site_fb_student_affairs import fetch_fb_student_affairs_posts

HISTORY_FILE = "sent_news_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def send_telegram_message(source, title, link):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("خطأ: مفاتيح تلجرام غير متوفرة في بيئة العمل.")
        return False
        
    text = (
        f"📢 *إعلان جديد من: {source}*\n\n"
        f"📌 *العنوان:* {title}\n\n"
        f"🔗 [اضغط هنا لقراءة التفاصيل والمنشور كاملاً]({link})"
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    try:
        res = requests.post(url, json=payload, timeout=15)
        return res.status_code == 200
    except Exception as e:
        print(f"فشل إرسال الإشعار لتلجرام: {e}")
        return False

def main():
    print("==================================================")
    print("...بدء عملية فحص إعلانات ومواقع الجامعة وصفحات فيسبوك...")
    print("==================================================")
    
    history = load_history()
    all_current_news = []
    
    # قائمة بجميع دوال فحص المواقع وفيسبوك
    checkers = [
        fetch_ju_official_news,
        fetch_ju_reg_bachelor_news,
        fetch_ju_reg_grad_news,
        fetch_ju_student_affairs_news,
        fetch_ju_community_service_news,
        fetch_ju_finance_news,
        fetch_ju_language_center_news,
        fetch_fb_student_affairs_posts
    ]
    
    for checker in checkers:
        try:
            items = checker()
            if items:
                all_current_news.extend(items)
        except Exception as e:
            print(f"خطأ أثناء فحص أحد المصادر: {e}")
            
    sent_count = 0
    new_history = list(history)
    
    for item in all_current_news:
        item_id = item.get("id")
        if item_id and item_id not in history:
            print(f"إعلان جديد تم اكتشافه: {item.get('title')}")
            if send_telegram_message(item['source'], item['title'], item['link']):
                print("-> تم إرسال الإشعار إلى تلجرام بنجاح.")
                new_history.append(item_id)
                sent_count += 1
                
    # الاحتفاظ بآخر 1000 معرف إعلان لتجنب تضخم الملف
    if len(new_history) > 1000:
        new_history = new_history[-1000:]
        
    save_history(new_history)
    
    print("==================================================")
    print(f"اكتمل الفحص بنجاح. عدد الإعلانات/المنشورات الجديدة المرسلة: {sent_count}")
    print("==================================================")

if __name__ == "__main__":
    main()

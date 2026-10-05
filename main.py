import os
import sys
import json
import requests
from bs4 import BeautifulSoup
import hashlib

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
        print(f"[تنبيه تجريبي] ({source}) -> {title[:40]}...", flush=True)
        return False
        
    text = (
        f"📢 *إعلان جديد من: {source}*\n\n"
        f"📌 *العنوان:* {title}\n\n"
        f"🔗 [اضغط هنا لقراءة تفاصيل الإعلان]({link})"
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
        print(f"فشل إرسال الإشعار لتيليجرام: {e}", flush=True)
        return False

def send_tg_channel_post(channel_name, post_text, post_link):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print(f"[منشور تيليجرام تجريبي] ({channel_name}) -> {post_text[:40]}...", flush=True)
        return False

    message_body = (
        f"📢 <b>منشور جديد من: {channel_name}</b>\n\n"
        f"{post_text}\n\n"
        f"🔗 <a href='{post_link}'>رابط المنشور الأصلي</a>"
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message_body,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    
    try:
        res = requests.post(url, json=payload, timeout=15)
        return res.status_code == 200
    except Exception as e:
        print(f"فشل إرسال منشور التيليجرام: {e}", flush=True)
        return False

def scrape_announcements(source_name, target_url, base_domain, prefix):
    items = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'ar,en;q=0.9'
    }
    
    ignore_texts = [
        "عرض الكل", "المزيد", "الصفحة الرئيسية", "رجوع", "السابق", "التالي", 
        "الرئيسية", "اتصل بنا", "عن الجامعة", "Home", "Back", "View All"
    ]
    
    try:
        res = requests.get(target_url, headers=headers, timeout=20)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            text = a.get_text(" ", strip=True)
            
            if len(text) < 12 or any(ignored == text for ignored in ignore_texts):
                continue
                
            is_announcement = any(k in href.lower() for k in [
                "dispform.aspx", "dispann", "school_dispann", "reg_dispann", "announcement"
            ])
            
            if is_announcement:
                if href.startswith("http"):
                    link = href
                else:
                    link = f"{base_domain.rstrip('/')}/{href.lstrip('/')}"
                    
                item_id = f"{prefix}_" + hashlib.md5((link + text).encode('utf-8')).hexdigest()[:12]
                
                if not any(i['id'] == item_id for i in items):
                    items.append({
                        'source': source_name,
                        'id': item_id,
                        'title': text,
                        'link': link
                    })
    except Exception as e:
        print(f"خطأ أثناء فحص {source_name}: {e}", flush=True)
        
    return items[:5]

# 1. إعلانات الجامعة الأردنية
def fetch_ju_official_ann():
    return scrape_announcements(
        "إعلانات الجامعة الأردنية",
        "https://www.ju.edu.jo/ar/arabic/Lists/Announcements/All_Ann.aspx",
        "https://www.ju.edu.jo",
        "ju_ann"
    )

# 2. القبول و التسجيل (بكالوريوس)
def fetch_reg_bachelor_ann():
    return scrape_announcements(
        "القبول والتسجيل (بكالوريوس)",
        "https://registration.ju.edu.jo/Lists/UnitAnnouncements/Reg_AllAnn.aspx",
        "https://registration.ju.edu.jo",
        "reg_bach"
    )

# 3. القبول و التسجيل (دراسات عليا)
def fetch_grad_studies_ann():
    return scrape_announcements(
        "كلية الدراسات العليا",
        "https://graduatestudies.ju.edu.jo/ar/arabic/Lists/AcademicNews/School_AllAnn.aspx",
        "https://graduatestudies.ju.edu.jo",
        "grad_ann"
    )

# 4. إعلانات عمادة شؤون الطلبة
def fetch_student_affairs_ann():
    return scrape_announcements(
        "عمادة شؤون الطلبة",
        "https://studentaffairs.ju.edu.jo/Lists/Announcements/School_AllAnn.aspx",
        "https://studentaffairs.ju.edu.jo",
        "sa_ann"
    )

# 5. إعلانات مركز التنمية وخدمة المجتمع
def fetch_community_service_ann():
    return scrape_announcements(
        "مركز التنمية وخدمة المجتمع",
        "https://lcndc.ju.edu.jo/ar/arabic/Lists/Announcements/AllAnn_new.aspx",
        "https://lcndc.ju.edu.jo",
        "lcndc_ann"
    )

# 6. إعلانات الوحدة المالية
def fetch_finance_ann():
    return scrape_announcements(
        "الوحدة المالية",
        "https://units.ju.edu.jo/ar/finance/Lists/Announcements/School_AllAnn.aspx",
        "https://units.ju.edu.jo",
        "fin_ann"
    )

# 7. إعلانات مركز اللغات
def fetch_languages_center_ann():
    return scrape_announcements(
        "مركز اللغات",
        "https://centers.ju.edu.jo/ar/ujlc/Lists/Announcements/School_AllAnn.aspx",
        "https://centers.ju.edu.jo",
        "lang_ann"
    )

# 8. فاحص قنوات تيليجرام
def scrape_telegram_channels():
    channels = [
        {"name": "قناة الجامعة الأردنية الرسمية", "username": "universityofjordanofficial"},
        {"name": "أخبار الجامعة الأردنية", "username": "JUposts"}
    ]
    
    posts = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36'
    }
    
    for ch in channels:
        url = f"https://t.me/s/{ch['username']}"
        try:
            res = requests.get(url, headers=headers, timeout=15)
            if res.status_code != 200:
                continue
                
            soup = BeautifulSoup(res.text, 'html.parser')
            messages = soup.find_all("div", class_="tgme_widget_message")
            
            for msg in messages[-3:]:
                data_post = msg.get("data-post")
                if not data_post:
                    continue
                    
                text_div = msg.find("div", class_="tgme_widget_message_text")
                post_text = text_div.get_text(separator="\n").strip() if text_div else ""
                
                if not post_text:
                    continue
                    
                post_id = f"tg_{data_post.replace('/', '_')}"
                posts.append({
                    "id": post_id,
                    "channel_name": ch["name"],
                    "text": post_text,
                    "link": f"https://t.me/{data_post}"
                })
        except Exception as e:
            print(f"خطأ أثناء فحص قناة تيليجرام {ch['username']}: {e}", flush=True)
            
    return posts

def main():
    print("==================================================", flush=True)
    print("...بدء فحص صفحات الإعلانات الرسمية وقنوات تيليجرام...", flush=True)
    print("==================================================", flush=True)
    
    history = load_history()
    new_history = list(history)
    sent_count = 0

    all_current_announcements = []
    scrapers = [
        fetch_ju_official_ann,
        fetch_reg_bachelor_ann,
        fetch_grad_studies_ann,
        fetch_student_affairs_ann,
        fetch_community_service_ann,
        fetch_finance_ann,
        fetch_languages_center_ann
    ]
    
    for scraper in scrapers:
        try:
            items = scraper()
            if items:
                all_current_announcements.extend(items)
        except Exception as e:
            print(f"خطأ أثناء تشغيل الفاحص: {e}", flush=True)
            
    print(f"إجمالي إعلانات المواقع: {len(all_current_announcements)}", flush=True)
    
    for item in all_current_announcements:
        item_id = item.get("id")
        if item_id and item_id not in history:
            print(f"-> [إعلان موقع جديد] {item['source']}: {item['title'][:60]}...", flush=True)
            if send_telegram_message(item['source'], item['title'], item['link']):
                print("   (تم الإرسال لتليجرام)", flush=True)
                new_history.append(item_id)
                sent_count += 1
            else:
                new_history.append(item_id)

    tg_posts = scrape_telegram_channels()
    print(f"إجمالي منشورات التيليجرام المفحوصة: {len(tg_posts)}", flush=True)
    
    for post in tg_posts:
        post_id = post.get("id")
        if post_id and post_id not in history:
            print(f"-> [منشور تيليجرام جديد] {post['channel_name']}: {post['text'][:50]}...", flush=True)
            if send_tg_channel_post(post["channel_name"], post["text"], post["link"]):
                print("   (تم الإرسال لتليجرام)", flush=True)
                new_history.append(post_id)
                sent_count += 1
            else:
                new_history.append(post_id)
                
    if len(new_history) > 2000:
        new_history = new_history[-2000:]
        
    save_history(new_history)
    
    print("==================================================", flush=True)
    print(f"اكتمل الفحص بنجاح! المنشورات والإعلانات الجديدة: {sent_count}", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    main()

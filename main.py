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
        print(f"فشل إرسال الإشعار لتيليجرام: {e}", flush=True)
        return False

def scrape_generic_ju(source_name, target_url, base_domain, prefix):
    items = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    }
    try:
        res = requests.get(target_url, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            
            # فلترة الكلمات الدالة على الإعلانات والأخبار
            keywords = ["newsdetails", "news", "announcement", "announce", "dispann", "school_dispann", "listform", "viewpost"]
            if any(k in href.lower() for k in keywords) and len(text) > 15:
                if href.startswith("http"):
                    link = href
                else:
                    link = f"{base_domain.rstrip('/')}/{href.lstrip('/')}"
                    
                item_id = f"{prefix}_" + hashlib.md5(link.encode()).hexdigest()[:10]
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

# 1. إعلانات الجامعة الرسمية
def fetch_ju_official():
    return scrape_generic_ju("إعلانات الجامعة الأردنية", "https://www.ju.edu.jo", "https://www.ju.edu.jo", "ju_main")

# 2. القبول والتسجيل (بكالوريوس)
def fetch_ju_registration():
    return scrape_generic_ju("القبول والتسجيل (بكالوريوس)", "https://registration.ju.edu.jo", "https://registration.ju.edu.jo", "ju_reg")

# 3. القبول والتسجيل (دراسات عليا)
def fetch_ju_grad_studies():
    return scrape_generic_ju("كلية الدراسات العليا", "https://graduatestudies.ju.edu.jo", "https://graduatestudies.ju.edu.jo", "ju_grad")

# 4. إعلانات العمادة
def fetch_ju_student_affairs():
    return scrape_generic_ju("عمادة شؤون الطلبة", "https://studentaffairs.ju.edu.jo", "https://studentaffairs.ju.edu.jo", "ju_sa")

# 5. إعلانات مركز التنمية وخدمة المجتمع
def fetch_ju_community_service():
    return scrape_generic_ju("مركز التنمية وخدمة المجتمع", "https://lcndc.ju.edu.jo", "https://lcndc.ju.edu.jo", "ju_lcndc")

# 6. إعلانات الوحدة المالية
def fetch_ju_finance():
    return scrape_generic_ju("الوحدة المالية", "https://units.ju.edu.jo/ar/finance", "https://units.ju.edu.jo", "ju_fin")

# 7. إعلانات مركز اللغات
def fetch_ju_languages_center():
    return scrape_generic_ju("مركز اللغات", "https://centers.ju.edu.jo/ar/ujlc/Home.aspx", "https://centers.ju.edu.jo", "ju_lang")

def main():
    print("==================================================", flush=True)
    print("...بدء فحص مواقع وإعلانات الجامعة المعتمدة (7 مواقع)...", flush=True)
    print("==================================================", flush=True)
    
    history = load_history()
    all_current_news = []
    
    scrapers = [
        fetch_ju_official,
        fetch_ju_registration,
        fetch_ju_grad_studies,
        fetch_ju_student_affairs,
        fetch_ju_community_service,
        fetch_ju_finance,
        fetch_ju_languages_center
    ]
    
    for scraper in scrapers:
        try:
            items = scraper()
            if items:
                all_current_news.extend(items)
        except Exception as e:
            print(f"خطأ أثناء تشغيل الفاحص: {e}", flush=True)
            
    print(f"إجمالي العناصر التي تم جلبها: {len(all_current_news)}", flush=True)
    
    sent_count = 0
    new_history = list(history)
    
    for item in all_current_news:
        item_id = item.get("id")
        if item_id and item_id not in history:
            print(f"-> [جديد] {item['source']}: {item['title'][:60]}...", flush=True)
            if send_telegram_message(item['source'], item['title'], item['link']):
                print("   (تم الإرسال لتليجرام)", flush=True)
                new_history.append(item_id)
                sent_count += 1
            else:
                new_history.append(item_id)
                
    if len(new_history) > 2000:
        new_history = new_history[-2000:]
        
    save_history(new_history)
    
    print("==================================================", flush=True)
    print(f"اكتمل الفحص بنجاح! الإعلانات الجديدة المسجلة: {sent_count}", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    main()

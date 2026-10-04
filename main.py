import os
import sys
import json
import requests
from bs4 import BeautifulSoup
import re
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

def fetch_ju_official():
    url = "https://www.ju.edu.jo"
    news_items = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(url, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if ("NewsDetails" in href or "news" in href.lower()) and len(text) > 15:
                link = href if href.startswith("http") else f"https://www.ju.edu.jo/{href.lstrip('/')}"
                item_id = "ju_main_" + hashlib.md5(link.encode()).hexdigest()[:10]
                if not any(i['id'] == item_id for i in news_items):
                    news_items.append({
                        'source': 'موقع الجامعة الأردنية الرئيسي',
                        'id': item_id,
                        'title': text,
                        'link': link
                    })
    except Exception as e:
        print(f"خطأ في فحص موقع الجامعة الرئيسي: {e}", flush=True)
    return news_items[:5]

def fetch_ju_registration():
    url = "https://registration.ju.edu.jo"
    news_items = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(url, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if any(k in href.lower() for k in ["announcement", "news", "viewpost"]) and len(text) > 15:
                link = href if href.startswith("http") else f"https://registration.ju.edu.jo/{href.lstrip('/')}"
                item_id = "ju_reg_" + hashlib.md5(link.encode()).hexdigest()[:10]
                if not any(i['id'] == item_id for i in news_items):
                    news_items.append({
                        'source': 'وحدة القبول والتسجيل',
                        'id': item_id,
                        'title': text,
                        'link': link
                    })
    except Exception as e:
        print(f"خطأ في فحص وحدة القبول والتسجيل: {e}", flush=True)
    return news_items[:5]

def fetch_ju_student_affairs_web():
    url = "https://studentaffairs.ju.edu.jo"
    news_items = []
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(url, headers=headers, timeout=15)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)
            if ("Announce" in href or "News" in href) and len(text) > 15:
                link = href if href.startswith("http") else f"https://studentaffairs.ju.edu.jo/{href.lstrip('/')}"
                item_id = "ju_sa_site_" + hashlib.md5(link.encode()).hexdigest()[:10]
                if not any(i['id'] == item_id for i in news_items):
                    news_items.append({
                        'source': 'موقع عمادة شؤون الطلبة',
                        'id': item_id,
                        'title': text,
                        'link': link
                    })
    except Exception as e:
        print(f"خطأ في فحص موقع شؤون الطلبة: {e}", flush=True)
    return news_items[:5]

def fetch_ju_student_affairs_facebook():
    """فحص منشورات صفحة فيسبوك لعمادة شؤون الطلبة"""
    print("[فحص فيسبوك]: بدء الاتصال بصفحة العمادة...", flush=True)
    posts = []
    
    # محاولة سحب التغذية المباشرة للصفحة
    try:
        fb_url = "https://www.facebook.com/plugins/page.php?href=https%3A%2F%2Fwww.facebook.com%2FStudentAffairsJU&tabs=timeline"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(fb_url, headers=headers, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            for div in soup.find_all('div', class_=re.compile(r'_1xnd|_4-u2|userContent')):
                txt = div.get_text(" ", strip=True)
                for w in ["إعجاب", "تعليق", "مشاركة", "Like", "Share"]:
                    txt = txt.replace(w, "")
                txt = re.sub(r'\s+', ' ', txt).strip()
                if len(txt) > 30 and not any(p['title'] == txt[:140] for p in posts):
                    post_id = "fb_sa_" + hashlib.md5(txt[:80].encode('utf-8')).hexdigest()[:12]
                    posts.append({
                        'source': 'فيسبوك: عمادة شؤون الطلبة',
                        'id': post_id,
                        'title': txt[:140] + ("..." if len(txt) > 140 else ""),
                        'link': "https://www.facebook.com/StudentAffairsJU"
                    })
    except Exception as e:
        print(f"[فحص فيسبوك]: خطأ في قراءة التغذية: {e}", flush=True)

    print(f"[فحص فيسبوك]: تم بنجاح إنهاء الفحص (المنشورات الملتقطة: {len(posts)}).", flush=True)
    return posts[:5]

def main():
    print("==================================================", flush=True)
    print("...بدء فحص مواقع الجامعة الرسمية وصفحة فيسبوك...", flush=True)
    print("==================================================", flush=True)
    
    history = load_history()
    all_current_news = []
    
    scrapers = [
        fetch_ju_official,
        fetch_ju_registration,
        fetch_ju_student_affairs_web,
        fetch_ju_student_affairs_facebook
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
                
    if len(new_history) > 1000:
        new_history = new_history[-1000:]
        
    save_history(new_history)
    
    print("==================================================", flush=True)
    print(f"اكتمل الفحص بنجاح! الإعلانات الجديدة المسجلة: {sent_count}", flush=True)
    print("==================================================", flush=True)

if __name__ == "__main__":
    main()

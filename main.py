import os
import sys
import json
import requests
from bs4 import BeautifulSoup
import re
import hashlib

HISTORY_FILE = "sent_news_history.json"

def load_history():
    """تحميل سجل الإعلانات السابقة لمنع التكرار"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history):
    """حفظ سجل الإعلانات"""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def send_telegram_message(source, title, link):
    """إرسال إشعار فوري عبر تيليجرام"""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print(f"[تنبيه] ({source}) -> {title[:50]}... (المفاتيح غير ممررة)")
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
        print(f"فشل إرسال الإشعار لتيليجرام: {e}")
        return False

def fetch_ju_official():
    """سحب أحدث أخبار البوابة الرئيسية للجامعة الأردنية"""
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
        print(f"خطأ في فحص موقع الجامعة الرئيسي: {e}")
    return news_items[:5]

def fetch_ju_registration():
    """سحب إعلانات وحدة القبول والتسجيل"""
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
        print(f"خطأ في فحص وحدة القبول والتسجيل: {e}")
    return news_items[:5]

def fetch_ju_student_affairs_web():
    """سحب إعلانات الموقع الرسمي لعمادة شؤون الطلبة"""
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
        print(f"خطأ في فحص موقع شؤون الطلبة: {e}")
    return news_items[:5]

def fetch_ju_student_affairs_facebook():
    """سحب أحدث منشورات صفحة فيسبوك لعمادة شؤون الطلبة عبر الكوكيز"""
    c_user = os.environ.get("FB_C_USER", "").strip()
    xs = os.environ.get("FB_XS", "").strip()
    
    if not c_user or not xs:
        print("[فحص فيسبوك]: كوكيز فيسبوك (FB_C_USER أو FB_XS) غير متوفرة في بيئة العمل.")
        return []

    print("[فحص فيسبوك]: جاري الاتصال بفيسبوك باستخدام الكوكيز...")
    url = "https://mbasic.facebook.com/StudentAffairsJU"
    posts = []
    cookies = {
        "c_user": c_user,
        "xs": xs,
        "locale": "ar_AR"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "ar,en;q=0.9",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document"
    }

    try:
        session = requests.Session()
        session.cookies.update(cookies)
        res = session.get(url, headers=headers, timeout=25)
        res.encoding = 'utf-8'

        if res.status_code == 200 and "login" not in res.url.lower():
            soup = BeautifulSoup(res.text, "html.parser")
            
            # البحث عن عناصر المقالات أو أوعية المنشورات في mbasic
            articles = soup.find_all("article") or soup.find_all("div", role="article")
            if not articles:
                articles = soup.find_all("div", id=re.compile(r'u_0_|story_'))

            for art in articles[:5]:
                text_content = art.get_text(" ", strip=True)
                clean_lines = [l for l in text_content.split(" ") if l not in ["إعجاب", "تعليق", "مشاركة", "Like", "Comment", "Share"]]
                post_text = " ".join(clean_lines).strip()

                if len(post_text) > 30:
                    link = "https://www.facebook.com/StudentAffairsJU"
                    for a in art.find_all("a", href=True):
                        href = a['href']
                        if any(k in href for k in ["story.php", "fbid=", "/posts/", "/photos/"]):
                            link = f"https://www.facebook.com{href}" if href.startswith("/") else href
                            break

                    post_id = "fb_sa_" + hashlib.md5(post_text[:100].encode('utf-8')).hexdigest()[:12]
                    if not any(p['id'] == post_id for p in posts):
                        posts.append({
                            'source': 'فيسبوك: عمادة شؤون الطلبة',
                            'id': post_id,
                            'title': post_text[:140] + ("..." if len(post_text) > 140 else ""),
                            'link': link
                        })
            print(f"[فحص فيسبوك]: تم بنجاح استخراج {len(posts)} منشور.")
        else:
            print(f"[فحص فيسبوك]: فشل الوصول للصفحة، الرابط المحول إليه: {res.url}")
    except Exception as e:
        print(f"[فحص فيسبوك]: حدث خطأ أثناء الاتصال: {e}")

    return posts[:5]

def main():
    print("==================================================")
    print("...بدء فحص مواقع الجامعة الرسمية وصفحة فيسبوك...")
    print("==================================================")
    
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
            print(f"خطأ أثناء تشغيل الفاحص: {e}")
            
    print(f"إجمالي العناصر التي تم جلبها: {len(all_current_news)}")
    
    sent_count = 0
    new_history = list(history)
    
    for item in all_current_news:
        item_id = item.get("id")
        if item_id and item_id not in history:
            print(f"-> [جديد] {item['source']}: {item['title'][:60]}...")
            if send_telegram_message(item['source'], item['title'], item['link']):
                print("   (تم الإرسال لتليجرام)")
                new_history.append(item_id)
                sent_count += 1
            else:
                new_history.append(item_id)
                
    if len(new_history) > 1000:
        new_history = new_history[-1000:]
        
    save_history(new_history)
    
    print("==================================================")
    print(f"اكتمل الفحص بنجاح! الإعلانات الجديدة المسجلة: {sent_count}")
    print("==================================================")

if __name__ == "__main__":
    main()

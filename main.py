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
    """سحب أحدث منشورات صفحة عمادة شؤون الطلبة عبر بوابة العرض وكوكيز الحساب"""
    c_user = os.environ.get("FB_C_USER", "").strip()
    xs = os.environ.get("FB_XS", "").strip()
    posts = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept-Language": "ar,ar-JO;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    # 1. المحاولة الأولى: بوابة تضمين الصفحة العامة الرسمية
    try:
        plugin_url = "https://www.facebook.com/plugins/page.php?href=https%3A%2F%2Fwww.facebook.com%2FStudentAffairsJU&tabs=timeline&locale=ar_AR"
        res_plugin = requests.get(plugin_url, headers=headers, timeout=20)
        if res_plugin.status_code == 200:
            soup = BeautifulSoup(res_plugin.text, "html.parser")
            containers = soup.find_all("div", class_=re.compile(r'_1xnd|_4-u2|userContent'))
            
            for container in containers:
                text_val = container.get_text(" ", strip=True)
                clean_lines = [l for l in text_val.split(" ") if l not in ["إعجاب", "تعليق", "مشاركة", "Like", "Share", "Comment"]]
                post_text = " ".join(clean_lines).strip()
                
                if len(post_text) > 35:
                    post_id = "fb_sa_" + hashlib.md5(post_text[:100].encode('utf-8')).hexdigest()[:12]
                    link = "https://www.facebook.com/StudentAffairsJU"
                    for a in container.find_all("a", href=True):
                        if any(k in a['href'] for k in ["/posts/", "/photos/", "story.php", "fbid="]):
                            link = f"https://www.facebook.com{a['href']}" if a['href'].startswith("/") else a['href']
                            break
                    if not any(p['id'] == post_id for p in posts):
                        posts.append({
                            'source': 'فيسبوك: عمادة شؤون الطلبة',
                            'id': post_id,
                            'title': post_text[:140] + ("..." if len(post_text) > 140 else ""),
                            'link': link
                        })
    except Exception as e:
        print(f"[فحص فيسبوك (بوابة التضمين)]: {e}")

    # 2. المحاولة الثانية: استخراج المنشورات عبر كوكيز الحساب من بيانات الصفحة المباشرة
    if not posts and c_user and xs:
        try:
            print("[فحص فيسبوك]: استخدام جلسة الكوكيز لقراءة المنشورات المحدثة...")
            session = requests.Session()
            session.cookies.update({"c_user": c_user, "xs": xs, "locale": "ar_AR"})
            res_fb = session.get("https://m.facebook.com/StudentAffairsJU", headers=headers, timeout=20)
            
            matches = re.findall(r'"message":\s*\{\s*"text":\s*"((?:\\.|[^"\\])+)"\}', res_fb.text)
            for m in matches[:5]:
                try:
                    decoded_text = json.loads(f'"{m}"')
                except Exception:
                    decoded_text = m.encode().decode('unicode_escape', errors='ignore')
                
                clean_text = re.sub(r'\s+', ' ', decoded_text).strip()
                if len(clean_text) > 35:
                    post_id = "fb_sa_" + hashlib.md5(clean_text[:100].encode('utf-8')).hexdigest()[:12]
                    if not any(p['id'] == post_id for p in posts):
                        posts.append({
                            'source': 'فيسبوك: عمادة شؤون الطلبة',
                            'id': post_id,
                            'title': clean_text[:140] + ("..." if len(clean_text) > 140 else ""),
                            'link': "https://www.facebook.com/StudentAffairsJU"
                        })
        except Exception as e:
            print(f"[فحص فيسبوك (كوكيز)]: {e}")

    print(f"[فحص فيسبوك]: تم بنجاح استخراج {len(posts)} منشور.")
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

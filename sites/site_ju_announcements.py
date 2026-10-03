import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def fetch_ju_announcements():
    """
    سحب الإعلانات الرسمية فقط لجامعة الأردن وتصفية روابط الموقع العامة
    """
    announcements = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ar,en;q=0.9'
    }

    # 1. فحص صفحة إعلانات الجامعة مع تتبع وسوم شيربوينت
    url = "https://www.ju.edu.jo/ar/arabic/Lists/Announcements/All_Ann.aspx"

    try:
        session = requests.Session()
        res = session.get(url, headers=headers, timeout=25)
        res.encoding = 'utf-8'

        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')

            # البحث عن عناصر الإعلانات في جداول شيربوينت
            for a in soup.find_all('a', href=True):
                href = a['href']
                title = a.get_text(strip=True)

                # التحقق من أن الرابط يخص تفاصيل إعلان في القائمة
                is_ann_link = ("DispForm.aspx" in href) or ("/Lists/Announcements/" in href and href.endswith(".aspx"))

                if is_ann_link and len(title) > 5 and "All_Ann" not in href:
                    full_link = urljoin("https://www.ju.edu.jo", href)
                    
                    # استخراج معرف فريد للإعلان
                    unique_id = full_link.lower().split("&")[0]

                    if not any(item['id'] == unique_id for item in announcements):
                        announcements.append({
                            'source': 'إعلانات الجامعة الأردنية',
                            'id': unique_id,
                            'title': title,
                            'link': full_link
                        })

            # إذا كانت الصفحة تستخدم تغذية RSS مدمجة للقائمة
            if not announcements:
                rss_url = "https://www.ju.edu.jo/ar/arabic/_layouts/15/listfeed.aspx?List=%7B5A0C6B59-D2BF-4C1F-9E04-0C64883A75E4%7D"
                rss_res = session.get(rss_url, headers=headers, timeout=15)
                if rss_res.status_code == 200:
                    rss_soup = BeautifulSoup(rss_res.content, 'xml')
                    items = rss_soup.find_all('item')
                    for it in items:
                        t = it.find('title')
                        l = it.find('link')
                        g = it.find('guid')
                        if t and l:
                            item_id = g.text.strip() if g else l.text.strip()
                            announcements.append({
                                'source': 'إعلانات الجامعة الأردنية',
                                'id': f"ju_rss_{item_id}",
                                'title': t.text.strip(),
                                'link': l.text.strip()
                            })

            print(f"تم العثور على {len(announcements)} إعلان رسمي.")

    except Exception as e:
        print(f"خطأ أثناء فحص الإعلانات: {e}")

    # إعادة أحدث الإعلانات فقط
    return announcements[:10]

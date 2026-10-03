import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def fetch_ju_announcements():
    """
    سحب أحدث الإعلانات من صفحة إعلانات الجامعة الأردنية
    """
    announcements = []
    
    # 1. تجربة جلب البيانات عبر SharePoint RSS / REST إذا توفر
    endpoints = [
        "https://www.ju.edu.jo/ar/arabic/Lists/Announcements/All_Ann.aspx",
        "https://www.ju.edu.jo/ar/arabic/_layouts/15/listfeed.aspx?List=%7B5A0C6B59-D2BF-4C1F-9E04-0C64883A75E4%7D"
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ar,en;q=0.9'
    }

    url = "https://www.ju.edu.jo/ar/arabic/Lists/Announcements/All_Ann.aspx"

    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=25)
        response.encoding = 'utf-8'

        print(f"كود الاستجابة من الجامعة الأردنية: {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # البحث عن الصفوف أو الجداول أو الروابط التي تحوي نصوص إعلانات
            for a in soup.find_all('a', href=True):
                title = a.get_text(strip=True)
                href = a['href']

                # تصفية الروابط العامة (مثل القوائم والرئيسية) والتركيز على نصوص الإعلانات الفعلية
                ignore_words = [
                    "الرئيسية", "عن الأردنية", "البحث العلمي", "القبول والتسجيل", 
                    "الخدمات الإدارية", "روابط سريعة", "English", "اتصل بنا", "المزيد"
                ]

                if len(title) >= 12 and not any(w in title for w in ignore_words):
                    full_url = urljoin("https://www.ju.edu.jo", href)
                    
                    # تمييز الإعلان إما بالرابط أو بعنوانه
                    ann_id = f"ju_ann_{hash(title)}"

                    if not any(item['id'] == ann_id for item in announcements):
                        announcements.append({
                            'source': 'إعلانات الجامعة الأردنية',
                            'id': ann_id,
                            'title': title,
                            'link': full_url
                        })

                        if len(announcements) >= 5:
                            break

            print(f"تم العثور على {len(announcements)} إعلان مرشح.")

    except Exception as e:
        print(f"خطأ أثناء فحص إعلانات الجامعة: {e}")

    return announcements

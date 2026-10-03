import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def fetch_ju_announcements():
    """
    سحب أحدث الإعلانات من صفحة إعلانات الجامعة الأردنية الرسمية
    """
    url = "https://www.ju.edu.jo/ar/arabic/Lists/Announcements/All_Ann.aspx"
    announcements = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ar,en-US;q=0.9,en;q=0.8'
    }

    try:
        response = requests.get(url, headers=headers, timeout=25)
        response.encoding = 'utf-8'

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # البحث عن جميع الروابط داخل الصفحة
            for a in soup.find_all('a', href=True):
                title = a.get_text(strip=True)
                href = a['href']

                # التأكد أن الرابط يخص إعلان وفيه عنوان واضح
                if "DispForm.aspx" in href and len(title) > 8:
                    full_url = urljoin("https://www.ju.edu.jo", href)

                    # استخراج المعرف الخاص بالإعلان
                    ann_id = full_url.lower()

                    # تجنب تكرار نفس الرابط في القائمة المستخرجة
                    if not any(item['id'] == ann_id for item in announcements):
                        announcements.append({
                            'source': 'إعلانات الجامعة الأردنية',
                            'id': ann_id,
                            'title': title,
                            'link': full_url
                        })

                        # نأخذ أحدث 5 إعلانات
                        if len(announcements) >= 5:
                            break

    except Exception as e:
        print(f"حدث خطأ أثناء فحص إعلانات الجامعة الأردنية: {e}")

    return announcements

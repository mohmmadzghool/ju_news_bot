import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

def fetch_ju_announcements():
    """
    سحب الإعلانات الرسمية فقط للجامعة الأردنية عبر مسار Disp_Ann.aspx
    """
    url = "https://www.ju.edu.jo/ar/arabic/Lists/Announcements/All_Ann.aspx"
    announcements = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'ar,en;q=0.9'
    }

    try:
        session = requests.Session()
        res = session.get(url, headers=headers, timeout=25)
        res.encoding = 'utf-8'

        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')

            # استهداف الروابط التي تحتوي حصراً على صفحة عرض الإعلان Disp_Ann.aspx
            for a in soup.find_all('a', href=True):
                href = a['href']
                title = a.get_text(strip=True)

                if "Disp_Ann.aspx" in href and "ID=" in href and len(title) > 3:
                    full_link = urljoin("https://www.ju.edu.jo/ar/arabic/Lists/Announcements/", href)
                    
                    # استخراج رقم الإعلان الفريد (مثل ID=122)
                    id_match = re.search(r'ID=(\d+)', href, re.IGNORECASE)
                    unique_id = f"ju_ann_{id_match.group(1)}" if id_match else full_link

                    if not any(item['id'] == unique_id for item in announcements):
                        announcements.append({
                            'source': 'إعلانات الجامعة الأردنية الرسمية',
                            'id': unique_id,
                            'title': title,
                            'link': full_link
                        })

            print(f"تم بنجاح جلب {len(announcements)} إعلان رسمي فعلي.")

    except Exception as e:
        print(f"خطأ أثناء فحص الإعلانات: {e}")

    # نأخذ أحدث 5 إعلانات
    return announcements[:5]

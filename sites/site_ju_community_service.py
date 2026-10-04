import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

def fetch_ju_community_service_announcements():
    """
    سحب إعلانات مركز التنمية وخدمة المجتمع الرسمية
    """
    url = "https://lcndc.ju.edu.jo/ar/arabic/Lists/Announcements/AllAnn_new.aspx"
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

            for a in soup.find_all('a', href=True):
                href = a['href']
                title = a.get_text(strip=True)

                is_ann_link = any(pattern in href for pattern in ["Disp_Ann.aspx", "School_DispAnn.aspx", "DispForm.aspx", "Ann_Disp.aspx", "Announcements"])

                if is_ann_link and "id=" in href.lower() and len(title) > 3:
                    full_link = urljoin("https://lcndc.ju.edu.jo/ar/arabic/Lists/Announcements/", href)
                    
                    id_match = re.search(r'id=(\d+)', href, re.IGNORECASE)
                    unique_id = f"ju_community_{id_match.group(1)}" if id_match else full_link

                    if not any(item['id'] == unique_id for item in announcements):
                        announcements.append({
                            'source': 'إعلانات مركز التنمية وخدمة المجتمع',
                            'id': unique_id,
                            'title': title,
                            'link': full_link
                        })

            print(f"تم بنجاح جلب {len(announcements)} إعلان من إعلانات مركز التنمية وخدمة المجتمع.")

    except Exception as e:
        print(f"خطأ أثناء فحص إعلانات مركز التنمية وخدمة المجتمع: {e}")

    return announcements[:5]

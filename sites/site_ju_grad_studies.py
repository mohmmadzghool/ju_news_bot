import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

def fetch_ju_grad_studies_announcements():
    """
    سحب إعلانات القبول وتسجيل (الدراسات العليا) الرسمية عبر نمط School_DispAnn.aspx
    """
    url = "https://graduatedstudies.ju.edu.jo/ar/arabic/Lists/AcademicNews/School_AllAnn.aspx"
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

                # النمط الدقيق المكتشف لصفحات إعلانات الدراسات العليا
                if "School_DispAnn.aspx" in href and "id=" in href.lower() and len(title) > 3:
                    full_link = urljoin("https://graduatedstudies.ju.edu.jo/ar/arabic/Lists/AcademicNews/", href)
                    
                    id_match = re.search(r'id=(\d+)', href, re.IGNORECASE)
                    unique_id = f"ju_grad_{id_match.group(1)}" if id_match else full_link

                    if not any(item['id'] == unique_id for item in announcements):
                        announcements.append({
                            'source': 'القبول وتسجيل (الدراسات العليا)',
                            'id': unique_id,
                            'title': title,
                            'link': full_link
                        })

            print(f"تم بنجاح جلب {len(announcements)} إعلان من القبول وتسجيل (الدراسات العليا).")

    except Exception as e:
        print(f"خطأ أثناء فحص إعلانات الدراسات العليا: {e}")

    return announcements[:5]

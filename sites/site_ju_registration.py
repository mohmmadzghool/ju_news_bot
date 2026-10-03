import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

def fetch_ju_registration_announcements():
    """
    سحب إعلانات وحدة القبول والتسجيل الرسمية (بكالوريوس) عبر نمط Reg_DispAnn.aspx
    """
    url = "https://registration.ju.edu.jo/Lists/UnitAnnouncements/Reg_AllAnn.aspx"
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

                if "Reg_DispAnn.aspx" in href and "ID=" in href and len(title) > 3:
                    full_link = urljoin("https://registration.ju.edu.jo/Lists/UnitAnnouncements/", href)
                    
                    id_match = re.search(r'ID=(\d+)', href, re.IGNORECASE)
                    unique_id = f"ju_reg_bach_{id_match.group(1)}" if id_match else full_link

                    if not any(item['id'] == unique_id for item in announcements):
                        announcements.append({
                            'source': 'القبول والتسجيل (بكالوريوس)',
                            'id': unique_id,
                            'title': title,
                            'link': full_link
                        })

            print(f"تم بنجاح جلب {len(announcements)} إعلان من القبول والتسجيل (بكالوريوس).")

    except Exception as e:
        print(f"خطأ أثناء فحص إعلانات القبول والتسجيل: {e}")

    return announcements[:5]

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

def fetch_ju_announcements():
    """
    سحب الإعلانات الرسمية فقط من جدول إعلانات الجامعة الأردنية
    """
    url = "https://www.ju.edu.jo/ar/arabic/Lists/Announcements/All_Ann.aspx"
    announcements = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ar,en;q=0.9'
    }

    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=25)
        response.encoding = 'utf-8'

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # 1. البحث عن الجدول الخاص بقائمة إعلانات SharePoint
            # SharePoint يعطي صفوف الجدول صنف ms-itmhover أو ms-listviewtable
            table = soup.find('table', {'class': lambda c: c and ('ms-listviewtable' in c or 'ms-summarycustombody' in c)})
            container = table if table else soup

            # 2. البحث عن الروابط الموجهة لصفحة تفاصيل الإعلان (DispForm.aspx?ID=)
            links = container.find_all('a', href=True)

            for a in links:
                href = a['href']
                title = a.get_text(strip=True)

                # الشرط الصارم للإعلان: رابط شيربوينت لعرض العنصر DispForm.aspx ومعه معرف رقمي
                if "DispForm.aspx" in href and "ID=" in href:
                    # استخراج رقم الإعلان الفريد من الرابط (مثال: ID=123)
                    id_match = re.search(r'ID=(\d+)', href, re.IGNORECASE)
                    if id_match and title and len(title) > 3:
                        item_id_num = id_match.group(1)
                        full_url = urljoin("https://www.ju.edu.jo", href)
                        unique_id = f"ju_official_ann_{item_id_num}"

                        if not any(item['id'] == unique_id for item in announcements):
                            announcements.append({
                                'source': 'إعلانات الجامعة الأردنية الرسمية',
                                'id': unique_id,
                                'title': title,
                                'link': full_url
                            })

            # في حال لم يجد عبر DispForm (إذا كان شيربوينت يعرض العناوين داخل خلايا ms-vb أو ms-vb2)
            if not announcements:
                for td in soup.find_all('td', {'class': lambda c: c and 'ms-vb' in c}):
                    a_tag = td.find('a', href=True)
                    if a_tag:
                        href = a_tag['href']
                        title = a_tag.get_text(strip=True)
                        if "ID=" in href and len(title) > 4:
                            id_match = re.search(r'ID=(\d+)', href, re.IGNORECASE)
                            item_id_num = id_match.group(1) if id_match else href
                            full_url = urljoin("https://www.ju.edu.jo", href)
                            unique_id = f"ju_official_ann_{item_id_num}"

                            if not any(item['id'] == unique_id for item in announcements):
                                announcements.append({
                                    'source': 'إعلانات الجامعة الأردنية الرسمية',
                                    'id': unique_id,
                                    'title': title,
                                    'link': full_url
                                })

            print(f"تم استخراج {len(announcements)} إعلان رسمي فعلي من الجدول.")

    except Exception as e:
        print(f"خطأ أثناء فحص إعلانات الجامعة: {e}")

    return announcements

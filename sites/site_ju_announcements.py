import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

def fetch_ju_announcements():
    """
    سحب الإعلانات الرسمية فقط من جدول إعلانات شيربوينت المباشر
    """
    url = "https://www.ju.edu.jo/ar/arabic/Lists/Announcements/All_Ann.aspx"
    announcements = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ar,en;q=0.9'
    }

    try:
        session = requests.Session()
        res = session.get(url, headers=headers, timeout=25)
        res.encoding = 'utf-8'

        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')

            # استهداف الروابط التي تحوي مسار الإعلان المباشر في شيربوينت
            for a in soup.find_all('a', href=True):
                href = a.get('href', '')
                title = a.get_text(strip=True)

                # الشرط الدقيق: الرابط يجب أن يكون داخل قائمة الإعلانات ويفتح صفحة عرض (DispForm)
                # أو يحتوي صراحة على معرف ID في قائمة الإعلانات
                is_ann_path = ('Lists/Announcements/DispForm.aspx' in href) or ('DispForm.aspx?ID=' in href)

                if is_ann_path and title:
                    # تصفية النصوص غير المفيدة مثل "تحرير" أو علامات النظام
                    if len(title) > 6 and not any(tag in title for tag in ['تعديل', 'تحرير', 'عرض']):
                        full_link = urljoin("https://www.ju.edu.jo", href)

                        # استخراج رقم ID الخاص بالإعلان
                        id_search = re.search(r'ID=(\d+)', href, re.IGNORECASE)
                        unique_id = f"ju_ann_{id_search.group(1)}" if id_search else full_link

                        if not any(item['id'] == unique_id for item in announcements):
                            announcements.append({
                                'source': 'إعلانات الجامعة الأردنية',
                                'id': unique_id,
                                'title': title,
                                'link': full_link
                            })

            # في حال كانت الصفحة لا تضع المسار كاملاً في href، استخراج من الجدول الأساسي
            if not announcements:
                content_tables = soup.find_all('table', {'class': lambda c: c and 'ms-listviewtable' in c})
                for tbl in content_tables:
                    for row in tbl.find_all('tr'):
                        a_elem = row.find('a', href=True)
                        if a_elem:
                            title = a_elem.get_text(strip=True)
                            href = a_elem.get('href', '')
                            if len(title) > 8 and 'All_Ann' not in href:
                                full_link = urljoin("https://www.ju.edu.jo", href)
                                announcements.append({
                                    'source': 'إعلانات الجامعة الأردنية',
                                    'id': full_link,
                                    'title': title,
                                    'link': full_link
                                })

            print(f"تم حصر {len(announcements)} إعلان رسمي فعلي.")

    except Exception as e:
        print(f"خطأ أثناء فحص الإعلانات: {e}")

    return announcements[:5]

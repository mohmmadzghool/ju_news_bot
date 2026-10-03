import requests
from bs4 import BeautifulSoup

def fetch_ju_announcements():
    """
    سحب أحدث الإعلانات من صفحة إعلانات الجامعة الأردنية الرسمية
    """
    url = "https://www.ju.edu.jo/ar/arabic/Lists/Announcements/All_Ann.aspx"
    announcements = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.encoding = 'utf-8'

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            # استخراج الروابط الخاصة بالإعلانات من الصفحة
            # روابط إعلانات الجامعة في شيربوينت تحتوي على DispForm.aspx?ID=
            links = soup.find_all('a', href=True)

            seen_ids = set()

            for a in links:
                href = a['href']
                title = a.get_text(strip=True)

                if "DispForm.aspx?ID=" in href and title:
                    # تحويل الرابط إلى رابط كامل إذا كان ناقصاً
                    if not href.startswith('http'):
                        full_url = "https://www.ju.edu.jo" + href
                    else:
                        full_url = href

                    # استخراج رقم الإعلان الفريد من الرابط
                    ann_id = full_url.split("ID=")[-1].split("&")[0]

                    if ann_id not in seen_ids:
                        seen_ids.add(ann_id)
                        announcements.append({
                            'source': 'إعلانات الجامعة الأردنية',
                            'id': f"ju_ann_{ann_id}",
                            'title': title,
                            'link': full_url
                        })

                        # نكتفي بأحدث 5 إعلانات في كل فحص
                        if len(announcements) >= 5:
                            break

    except Exception as e:
        print(f"حدث خطأ أثناء فحص إعلانات الجامعة الأردنية: {e}")

    return announcements
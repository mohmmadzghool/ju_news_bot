import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def fetch_ju_announcements():
    """
    سحب الإعلانات الرسمية فقط وتصفية القوائم الثابتة
    """
    url = "https://www.ju.edu.jo/ar/arabic/Lists/Announcements/All_Ann.aspx"
    announcements = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept-Language': 'ar,en;q=0.9'
    }

    # قائمة الكلمات والروابط الثابتة التي يجب تجاهلها تماماً
    ignored_keywords = [
        "الرئيسية", "عن الأردنية", "البحث العلمي", "القبول والتسجيل", 
        "الخدمات الإدارية", "روابط سريعة", "English", "اتصل بنا", "المزيد",
        "كيفية الالتحاق", "التسجيل الذاتي", "نظام إدارة المحتوى", "مستشفى الجامعة",
        "أخبار الجامعة", "البريد الإلكتروني", "بوابة الطالب", "بوابة الموظف",
        "المكتبة", "الكليات", "المراكز", "العمادات", "خريطة الموقع"
    ]

    try:
        session = requests.Session()
        res = session.get(url, headers=headers, timeout=25)
        res.encoding = 'utf-8'

        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')

            for a in soup.find_all('a', href=True):
                title = a.get_text(strip=True)
                href = a['href']

                # شروط الإعلان الحقيقي:
                # 1. عنوان كافي (أكثر من 15 حرف) ليكون جملة إعلان وليس زر أو رابط قائمة
                # 2. ألا يحتوي على أي كلمة من الكلمات الثابتة المستبعدة
                # 3. ألا يكون رابط فارغ أو مجرد علامة #
                if len(title) >= 15 and not any(word in title for word in ignored_keywords):
                    if not href.startswith('#') and not href.startswith('javascript:'):
                        full_link = urljoin("https://www.ju.edu.jo", href)
                        
                        # نعتمد عنوان الإعلان كمعرّف لمنع تكراره
                        ann_id = f"ju_{title[:30]}"

                        if not any(item['title'] == title for item in announcements):
                            announcements.append({
                                'source': 'إعلانات الجامعة الأردنية',
                                'id': ann_id,
                                'title': title,
                                'link': full_link
                            })

            print(f"تم جلب {len(announcements)} إعلان رسمي فعلي.")

    except Exception as e:
        print(f"خطأ أثناء فحص الإعلانات: {e}")

    # نأخذ أحدث 5 إعلانات مطابقة
    return announcements[:5]

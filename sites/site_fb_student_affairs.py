import os
import requests
from bs4 import BeautifulSoup
import re
import hashlib

def fetch_fb_student_affairs_posts():
    """
    سحب منشورات صفحة فيسبوك لعمادة شؤون الطلبة
    """
    url = "https://mbasic.facebook.com/StudentAffairsJU"
    posts = []

    c_user = os.environ.get("FB_C_USER", "").strip()
    xs = os.environ.get("FB_XS", "").strip()

    if not c_user or not xs:
        print("تنبيه: كوكيز فيسبوك غير متوفرة في إعدادات البيئة (GitHub Secrets).")
        return []

    cookies = {
        "c_user": c_user,
        "xs": xs
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "ar,en;q=0.9",
        "Sec-Fetch-Site": "same-origin"
    }

    try:
        session = requests.Session()
        session.cookies.update(cookies)

        res = session.get(url, headers=headers, timeout=25)
        res.encoding = 'utf-8'

        if res.status_code == 200 and "login" not in res.url.lower():
            soup = BeautifulSoup(res.text, "html.parser")

            # استخراج المقالات والمنشورات من واجهة mbasic
            articles = soup.find_all("article") or soup.find_all("div", role="article")
            
            if not articles:
                # محاولة إيجاد المنشورات عبر روابط التعليقات أو الروابط المباشرة
                articles = soup.find_all("div", id=re.compile(r'u_0_|story_'))

            for art in articles[:5]:
                text_content = art.get_text(" ", strip=True)
                
                # تصفية النصوص غير المفيدة
                clean_lines = [l for l in text_content.split(" ") if l not in ["إعجاب", "تعليق", "مشاركة", "Like", "Comment", "Share"]]
                post_text = " ".join(clean_lines).strip()

                if len(post_text) > 30:
                    # استخراج رابط المنشور إن وجد
                    link = "https://www.facebook.com/StudentAffairsJU"
                    for a in art.find_all("a", href=True):
                        if any(k in a['href'] for k in ["story.php", "fbid=", "/posts/", "/photos/"]):
                            link = f"https://www.facebook.com{a['href']}" if a['href'].startswith("/") else a['href']
                            break

                    post_id = "fb_sa_" + hashlib.md5(post_text[:100].encode('utf-8')).hexdigest()[:12]

                    if not any(p['id'] == post_id for p in posts):
                        posts.append({
                            'source': 'فيسبوك: عمادة شؤون الطلبة',
                            'id': post_id,
                            'title': post_text[:140] + ("..." if len(post_text) > 140 else ""),
                            'link': link
                        })

            print(f"تم بنجاح جلب {len(posts)} منشور من صفحة فيسبوك لعمادة شؤون الطلبة.")
        else:
            print("تعذر فتح صفحة فيسبوك: تم التحويل إلى تسجيل الدخول.")

    except Exception as e:
        print(f"خطأ أثناء فحص صفحة فيسبوك لعمادة شؤون الطلبة: {e}")

    return posts[:5]

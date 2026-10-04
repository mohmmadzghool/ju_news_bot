def fetch_ju_student_affairs_facebook():
    """سحب أحدث منشورات صفحة عمادة شؤون الطلبة"""
    c_user = os.environ.get("FB_C_USER", "").strip()
    xs = os.environ.get("FB_XS", "").strip()
    posts = []

    ignored_phrases = [
        "غير متوفر على هذا المتصفح",
        "انتقال إلى الصفحة الرئيسية",
        "تسجيل الدخول",
        "Log in",
        "إنشاء حساب",
        "شروط الخدمة",
        "سياسة الخصوصية",
        "مركز المساعدة"
    ]

    if not c_user or not xs:
        print("[فحص فيسبوك]: الكوكيز غير متوفرة.", flush=True)
        return []

    print("[فحص فيسبوك]: بدء الاتصال بصفحة فيسبوك...", flush=True)
    try:
        session = requests.Session()
        session.cookies.update({
            "c_user": c_user,
            "xs": xs,
            "locale": "ar_AR"
        })
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
            "Accept-Language": "ar,en;q=0.9"
        }
        res = session.get("https://mbasic.facebook.com/StudentAffairsJU?v=timeline", headers=headers, timeout=20)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, "html.parser")

        # فحص كافة الأقسام التي تحتوي على نصوص وروابط المنشورات
        for el in soup.find_all(['div', 'p', 'span']):
            text = el.get_text(" ", strip=True)
            for w in ["إعجاب", "تعليق", "مشاركة", "Like", "Comment", "Share", "·"]:
                text = text.replace(w, "")
            text = re.sub(r'\s+', ' ', text).strip()

            if 40 <= len(text) <= 600 and not any(phrase in text for phrase in ignored_phrases):
                # البحث عن رابط مرفق
                link = "https://www.facebook.com/StudentAffairsJU"
                parent = el.find_parent('div') or el
                for a in parent.find_all('a', href=True):
                    h = a['href']
                    if any(k in h for k in ["story.php", "fbid=", "/posts/", "/photos/"]):
                        link = f"https://www.facebook.com{h}" if h.startswith("/") else h
                        break

                post_id = "fb_sa_" + hashlib.md5(text[:80].encode('utf-8')).hexdigest()[:12]
                if not any(p['id'] == post_id for p in posts):
                    posts.append({
                        'source': 'فيسبوك: عمادة شؤون الطلبة',
                        'id': post_id,
                        'title': text[:140] + ("..." if len(text) > 140 else ""),
                        'link': link
                    })
            if len(posts) >= 5:
                break

    except Exception as e:
        print(f"[فحص فيسبوك]: تنبيه: {e}", flush=True)

    print(f"[فحص فيسبوك]: تم بنجاح استخراج {len(posts)} منشور حقيقي.", flush=True)
    return posts

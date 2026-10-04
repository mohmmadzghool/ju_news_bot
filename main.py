def fetch_ju_student_affairs_facebook():
    """سحب أحدث منشورات صفحة عمادة شؤون الطلبة عبر واجهة mbasic المخصصة"""
    c_user = os.environ.get("FB_C_USER", "").strip()
    xs = os.environ.get("FB_XS", "").strip()
    
    if not c_user or not xs:
        print("[فحص فيسبوك]: لم يتم العثور على الكوكيز FB_C_USER / FB_XS.")
        return []

    print("[فحص فيسبوك]: جاري الاتصال بواجهة mbasic عبر الكوكيز...")
    url = "https://mbasic.facebook.com/StudentAffairsJU"
    posts = []
    
    cookies = {
        "c_user": c_user,
        "xs": xs,
        "locale": "ar_AR"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document"
    }

    try:
        session = requests.Session()
        session.cookies.update(cookies)
        res = session.get(url, headers=headers, timeout=25)
        res.encoding = 'utf-8'

        if res.status_code == 200 and "login" not in res.url.lower():
            soup = BeautifulSoup(res.text, "html.parser")
            
            # البحث عن منشورات mbasic بكافة تقسيماتها
            articles = soup.find_all("article")
            if not articles:
                articles = soup.find_all("div", role="article")
            if not articles:
                articles = soup.find_all("div", id=re.compile(r'u_0_|story_'))

            for art in articles[:8]:
                # تجاهل أزرار الإعجاب والتعليق
                text_content = art.get_text(" ", strip=True)
                for stop_word in ["إعجاب", "تعليق", "مشاركة", "Like", "Comment", "Share", "·"]:
                    text_content = text_content.replace(stop_word, "")
                
                clean_lines = [w for w in text_content.split() if len(w) > 1]
                post_text = " ".join(clean_lines).strip()

                if len(post_text) >= 25:
                    link = "https://www.facebook.com/StudentAffairsJU"
                    for a in art.find_all("a", href=True):
                        href = a['href']
                        if any(k in href for k in ["story.php", "fbid=", "/posts/", "/photos/"]):
                            if href.startswith("/"):
                                link = f"https://www.facebook.com{href.split('?')[0] if 'story.php' not in href else href}"
                            else:
                                link = href
                            break

                    post_id = "fb_sa_" + hashlib.md5(post_text[:80].encode('utf-8')).hexdigest()[:12]
                    if not any(p['id'] == post_id for p in posts):
                        posts.append({
                            'source': 'فيسبوك: عمادة شؤون الطلبة',
                            'id': post_id,
                            'title': post_text[:140] + ("..." if len(post_text) > 140 else ""),
                            'link': link
                        })
            print(f"[فحص فيسبوك]: تم بنجاح استخراج {len(posts)} منشور.")
        else:
            print(f"[فحص فيسبوك]: تم تحويل الطلب أو فشل (URL: {res.url[:45]}...)")
    except Exception as e:
        print(f"[فحص فيسبوك]: حدث خطأ أثناء الاتصال: {e}")

    return posts[:5]

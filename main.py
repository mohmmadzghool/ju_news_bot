def fetch_ju_student_affairs_facebook():
    """سحب منشورات صفحة عمادة شؤون الطلبة عبر واجهة البيانات السريعة"""
    c_user = os.environ.get("FB_C_USER", "").strip()
    xs = os.environ.get("FB_XS", "").strip()
    posts = []

    # 1. جلب المنشورات عبر جسر RSS المفتوح لصفحة عمادة شؤون الطلبة
    rss_urls = [
        "https://rsshub.app/facebook/page/StudentAffairsJU",
        "https://rss.app/feeds/StudentAffairsJU.xml"
    ]
    
    for r_url in rss_urls:
        try:
            r = requests.get(r_url, timeout=12)
            if r.status_code == 200 and "<item>" in r.text:
                soup = BeautifulSoup(r.text, "xml")
                for item in soup.find_all("item")[:5]:
                    title_elem = item.find("title") or item.find("description")
                    link_elem = item.find("link")
                    if title_elem:
                        clean_text = BeautifulSoup(title_elem.text, "html.parser").get_text(strip=True)
                        clean_text = re.sub(r'\s+', ' ', clean_text)
                        if len(clean_text) > 25:
                            item_link = link_elem.text.strip() if link_elem else "https://www.facebook.com/StudentAffairsJU"
                            post_id = "fb_sa_" + hashlib.md5(clean_text[:80].encode('utf-8')).hexdigest()[:12]
                            posts.append({
                                'source': 'فيسبوك: عمادة شؤون الطلبة',
                                'id': post_id,
                                'title': clean_text[:140] + ("..." if len(clean_text) > 140 else ""),
                                'link': item_link
                            })
                if posts:
                    print(f"[فحص فيسبوك]: تم بنجاح استخراج {len(posts)} منشور عبر التغذية المباشرة.", flush=True)
                    return posts
        except Exception:
            pass

    # 2. في حال لم يتوفر الرابط، يتم استخدام جلسة الكوكيز مع تجاوز صفحة الموافقة
    if c_user and xs:
        try:
            session = requests.Session()
            session.cookies.update({
                "c_user": c_user,
                "xs": xs,
                "locale": "ar_AR",
                "datr": "test"
            })
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                "Accept-Language": "ar,en;q=0.9"
            }
            res = session.get("https://mbasic.facebook.com/StudentAffairsJU?v=timeline", headers=headers, timeout=20)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, "html.parser")
            
            for a in soup.find_all("a", href=True):
                h = a['href']
                t = a.get_text(strip=True)
                if any(k in h for k in ["story.php", "fbid=", "/posts/"]) and len(t) > 30:
                    post_id = "fb_sa_" + hashlib.md5(t[:80].encode('utf-8')).hexdigest()[:12]
                    link = f"https://www.facebook.com{h}" if h.startswith("/") else h
                    if not any(p['id'] == post_id for p in posts):
                        posts.append({
                            'source': 'فيسبوك: عمادة شؤون الطلبة',
                            'id': post_id,
                            'title': t[:140] + ("..." if len(t) > 140 else ""),
                            'link': link
                        })
            print(f"[فحص فيسبوك]: تم بنجاح استخراج {len(posts)} منشور.", flush=True)
        except Exception as e:
            print(f"[فحص فيسبوك]: خطأ: {e}", flush=True)

    return posts[:5]

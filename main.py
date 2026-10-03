from sites.site_ju_announcements import fetch_ju_announcements
from storage import load_sent_ids, save_sent_ids
from telegram_notifier import send_telegram_alert

def main():
    print("=" * 45)
    print("بدء عملية فحص إعلانات ومواقع الجامعة الأردنية...")
    print("=" * 45)

    # 1. تحميل قائمة الإعلانات التي تم إرسالها سابقاً
    sent_ids = load_sent_ids()
    new_found_count = 0

    # 2. قائمة دوال فحص المواقع (سنضيف هنا المواقع الباقية تباعاً)
    scrapers = [
        fetch_ju_announcements,
    ]

    # 3. المرور على كل موقع وفحص إعلاناته
    for scraper in scrapers:
        try:
            items = scraper()
            print(f"تم جلب {len(items)} عنصر من أحد المصادر.")

            for item in items:
                item_id = item['id']

                # إذا لم يتم إرسال هذا الإعلان من قبل
                if item_id not in sent_ids:
                    print(f"إعلان جديد تم اكتشافه: {item['title']}")
                    
                    success = send_telegram_alert(
                        source=item['source'],
                        title=item['title'],
                        link=item['link']
                    )

                    if success:
                        sent_ids.add(item_id)
                        new_found_count += 1
                        print("-> تم إرسال الإشعار إلى تلجرام بنجاح.")
                    else:
                        print("-> فشل إرسال الإشعار إلى تلجرام.")

        except Exception as e:
            print(f"حدث خطأ أثناء تشغيل الفاحص: {e}")

    # 4. حفظ قائمة الإعلانات المحدثة لمنع التكرار مستقبلاً
    save_sent_ids(sent_ids)
    print("=" * 45)
    print(f"اكتمل الفحص بنجاح. عدد الإعلانات الجديدة المرسلة: {new_found_count}")
    print("=" * 45)

if __name__ == "__main__":
    main()
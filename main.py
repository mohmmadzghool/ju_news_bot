from sites.site_ju_announcements import fetch_ju_announcements
from sites.site_ju_registration import fetch_ju_registration_announcements
from sites.site_ju_grad_studies import fetch_ju_grad_studies_announcements
from sites.site_ju_student_affairs import fetch_ju_student_affairs_announcements
from sites.site_ju_community_service import fetch_ju_community_service_announcements
from sites.site_ju_finance import fetch_ju_finance_announcements
from sites.site_ju_language_center import fetch_ju_language_center_announcements
from telegram_notifier import send_telegram_alert
from storage import load_sent_ids, save_sent_ids

def main():
    print("==================================================")
    print("بدء عملية فحص إعلانات ومواقع الجامعة الأردنية...")
    print("==================================================")

    sent_ids = load_sent_ids()
    new_sent_ids = list(sent_ids)
    new_items_count = 0

    fetchers = [
        fetch_ju_announcements,
        fetch_ju_registration_announcements,
        fetch_ju_grad_studies_announcements,
        fetch_ju_student_affairs_announcements,
        fetch_ju_community_service_announcements,
        fetch_ju_finance_announcements,
        fetch_ju_language_center_announcements
    ]

    for fetcher in fetchers:
        try:
            items = fetcher()
            for item in items:
                item_id = item['id']
                if item_id not in sent_ids:
                    print(f"إعلان جديد تم اكتشافه: {item['title']}")
                    
                    success = send_telegram_alert(
                        source=item['source'],
                        title=item['title'],
                        link=item['link']
                    )
                    
                    if success:
                        print("-> تم إرسال الإشعار إلى تلجرام بنجاح.")
                        new_sent_ids.append(item_id)
                        new_items_count += 1
                    else:
                        print("-> فشل إرسال الإشعار إلى تلجرام.")
        except Exception as e:
            print(f"خطأ أثناء تشغيل الفاحص: {e}")

    if new_items_count > 0:
        save_sent_ids(new_sent_ids)

    print("==================================================")
    print(f"اكتمل الفحص بنجاح. عدد الإعلانات الجديدة المرسلة: {new_items_count}")
    print("==================================================")

if __name__ == "__main__":
    main()

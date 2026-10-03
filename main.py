import os
import html
from sites.site_ju_announcements import fetch_ju_announcements
from sites.site_ju_registration import fetch_ju_registration_announcements
import telegram_notifier
from storage import load_sent_ids, save_sent_ids

def notify(msg):
    try:
        if hasattr(telegram_notifier, 'send_telegram_message'):
            return telegram_notifier.send_telegram_message(msg)
        elif hasattr(telegram_notifier, 'send_telegram_notification'):
            return telegram_notifier.send_telegram_notification(msg)
        elif hasattr(telegram_notifier, 'send_message'):
            return telegram_notifier.send_message(msg)
        elif hasattr(telegram_notifier, 'send_notification'):
            return telegram_notifier.send_notification(msg)
    except Exception as e:
        print(f"حدث خطأ أثناء الإرسال لتلجرام: {e}")
    return False

def main():
    print("==================================================")
    print("بدء عملية فحص إعلانات ومواقع الجامعة الأردنية...")
    print("==================================================")

    sent_ids = load_sent_ids()
    new_sent_ids = list(sent_ids)
    new_items_count = 0

    fetchers = [
        fetch_ju_announcements,
        fetch_ju_registration_announcements
    ]

    for fetcher in fetchers:
        try:
            items = fetcher()
            for item in items:
                item_id = item['id']
                if item_id not in sent_ids:
                    print(f"إعلان جديد تم اكتشافه: {item['title']}")
                    
                    # تنظيف النصوص لمنع أخطاء التنسيق في تلجرام
                    source_title = html.escape(item['source'])
                    ann_title = html.escape(item['title'])
                    
                    msg = (
                        f"📢 <b>{source_title}</b>\n\n"
                        f"📌 {ann_title}\n\n"
                        f"🔗 <a href='{item['link']}'>اضغط هنا لقراءة التفاصيل</a>"
                    )
                    
                    success = notify(msg)
                    if success:
                        print("-> تم إرسال الإشعار إلى تلجرام بنجاح.")
                        new_sent_ids.append(item_id)
                        new_items_count += 1
                    else:
                        print("-> فشل إرسال الإشعار، يرجى فحص دالة تلجرام.")
        except Exception as e:
            print(f"خطأ أثناء تشغيل الفاحص: {e}")

    if new_items_count > 0:
        save_sent_ids(new_sent_ids)

    print("==================================================")
    print(f"اكتمل الفحص بنجاح. عدد الإعلانات الجديدة المرسلة: {new_items_count}")
    print("==================================================")

if __name__ == "__main__":
    main()

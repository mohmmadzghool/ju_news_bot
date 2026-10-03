import json
import os

HISTORY_FILE = "sent_news_history.json"

def load_sent_ids():
    """قراءة قائمة معرّفات الأخبار المرسلة سابقاً"""
    if not os.path.exists(HISTORY_FILE):
        return set()
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return set(data)
    except Exception as e:
        print(f"تنبيه: تعذر قراءة سجل الأخبار القديم ({e})، سيتم إنشاء سجل جديد.")
        return set()

def save_sent_ids(sent_ids):
    """حفظ قائمة المعرّفات المحدّثة في الملف"""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(list(sent_ids), f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"خطأ أثناء حفظ السجل: {e}")
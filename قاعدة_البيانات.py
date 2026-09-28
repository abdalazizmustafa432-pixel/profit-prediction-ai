import sqlite3

# إنشاء قاعدة البيانات
conn = sqlite3.connect("المستخدمون.db")

cursor = conn.cursor()

# إنشاء جدول المستخدمين
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# إنشاء حساب تجريبي
try:
    cursor.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        ("admin", "1234")
    )
except sqlite3.IntegrityError:
    pass

# حفظ التغييرات
conn.commit()

# إغلاق قاعدة البيانات
conn.close()

print("تم إنشاء قاعدة بيانات المستخدمين بنجاح.")
print("اسم المستخدم: admin")
print("كلمة المرور: 1234")
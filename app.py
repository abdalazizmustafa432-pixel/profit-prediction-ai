from flask import Flask, render_template, request, redirect, session
import sqlite3
import joblib
import pandas as pd

app = Flask(__name__)

# مفتاح الجلسة
app.secret_key = "مفتاح_سري_للمشروع"

# تحميل نموذج الذكاء الاصطناعي
model = joblib.load("النموذج/نموذج_التنبؤ_بالأرباح.pkl")


# إنشاء قاعدة البيانات وجدول المستخدمين تلقائيًا
def init_database():

    conn = sqlite3.connect("المستخدمون.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # إنشاء مستخدم افتراضي إذا كانت قاعدة البيانات جديدة
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", "1234")
        )

    conn.commit()
    conn.close()


# تهيئة قاعدة البيانات عند تشغيل النظام
init_database()


# الصفحة الرئيسية
@app.route("/")
def home():

    if "username" not in session:
        return redirect("/login")

    return render_template("index.html")


# تسجيل الدخول
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("المستخدمون.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session["username"] = username

            return redirect("/")

        return render_template(
            "login.html",
            error="اسم المستخدم أو كلمة المرور غير صحيحة"
        )

    return render_template("login.html")


# التنبؤ بالأرباح
@app.route("/predict", methods=["POST"])
def predict():

    if "username" not in session:
        return redirect("/login")

    sales = float(request.form["sales"])
    quantity = int(request.form["quantity"])
    discount = float(request.form["discount"])
    shipping_cost = float(request.form["shipping_cost"])
    year = int(request.form["year"])
    weeknum = int(request.form["weeknum"])

    # إنشاء بيانات العملية
    data = pd.DataFrame([{
        "Sales": sales,
        "Quantity": quantity,
        "Discount": discount,
        "Shipping.Cost": shipping_cost,
        "Year": year,
        "weeknum": weeknum
    }])

    # إضافة الأعمدة التي يحتاجها النموذج
    for column in model.feature_names_in_:

        if column not in data.columns:
            data[column] = 0

    # ترتيب الأعمدة بنفس ترتيب التدريب
    data = data[model.feature_names_in_]

    # تنفيذ التنبؤ
    prediction = model.predict(data)

    profit = round(prediction[0], 2)

    # عرض النتيجة في نفس الصفحة
    return render_template(
        "index.html",
        profit=profit
    )


# تسجيل الخروج
@app.route("/logout")
def logout():

    session.pop("username", None)

    return redirect("/login")


# تشغيل النظام
if __name__ == "__main__":
    app.run(debug=True)
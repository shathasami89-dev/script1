from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# إعداد التطبيق
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leaks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# نموذج قاعدة البيانات للأهداف
class Target(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)

# نموذج سجل الفحوصات
class ScanResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_email = db.Column(db.String(120))
    found = db.Column(db.Boolean)
    details = db.Column(db.Text)
    scanned_at = db.Column(db.DateTime, default=datetime.utcnow)

# قائمة وهمية للتجربة (محاكاة التسريبات)
fake_leaks = {
    "leaked@example.com": "تم العثور على تسريب من Adobe و LinkedIn",
    "oldbreach@example.com": "تم العثور على تسريب من Dropbox",
    "shatha@example.com": "تم العثور على تسريب من TestBreach"
}

# قالب HTML
INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>مراقبة تسريبات البيانات</title>
    <style>
        body { font-family: Arial; margin: 20px; background: #f4f4f4; }
        .container { max-width: 800px; margin: auto; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px #ccc; }
        input[type=text] { width: 70%; padding: 8px; }
        button { padding: 8px 12px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: center; }
        th { background: #eee; }
        .result { margin-top: 20px; padding: 10px; border-radius: 5px; }
        .success { background-color: #d4edda; color: #155724; }
        .warning { background-color: #fff3cd; color: #856404; }
    </style>
</head>
<body>
<div class="container">
    <h2>مراقبة تسريبات البيانات</h2>
    <form method="POST" action="/add">
        <input type="text" name="email" placeholder="أدخل البريد الإلكتروني" required>
        <button type="submit">إضافة</button>
    </form>

    <h3>قائمة الأهداف</h3>
    <table>
        <tr><th>ID</th><th>البريد</th><th>تاريخ الإضافة</th></tr>
        {% for t in targets %}
        <tr>
            <td>{{ t.id }}</td>
            <td>{{ t.email }}</td>
            <td>{{ t.added_at.strftime('%Y-%m-%d %H:%M') }}</td>
        </tr>
        {% endfor %}
    </table>

    <form method="POST" action="/scan">
        <button type="submit" style="margin-top: 20px;">فحص التسريبات</button>
    </form>

    {% if results %}
        {% for r in results %}
            <div class="result {% if r.found %}warning{% else %}success{% endif %}">
                البريد: {{ r.target_email }} -
                {% if r.found %} {{ r.details }} {% else %} آمن {% endif %}
            </div>
        {% endfor %}
    {% endif %}
</div>
</body>
</html>
"""

# الصفحة الرئيسية
@app.route("/")
def index():
    targets = Target.query.all()
    return render_template_string(INDEX_HTML, targets=targets, results=None)

# إضافة بريد
@app.route("/add", methods=["POST"])
def add():
    email = request.form.get("email")
    if email:
        if not Target.query.filter_by(email=email).first():
            new_target = Target(email=email)
            db.session.add(new_target)
            db.session.commit()
    return redirect(url_for("index"))

# فحص جميع الأهداف (وهمي)
def check_email_leak(email):
    if email in fake_leaks:
        return True, fake_leaks[email]
    return False, ""

@app.route("/scan", methods=["POST"])
def scan():
    targets = Target.query.all()
    results = []
    for t in targets:
        found, details = check_email_leak(t.email)
        result = ScanResult(target_email=t.email, found=found, details=details)
        db.session.add(result)
        results.append(result)
    db.session.commit()
    return render_template_string(INDEX_HTML, targets=targets, results=results)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

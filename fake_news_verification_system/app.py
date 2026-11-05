import os, re, sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from model_utils import predict_news

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "news.db")
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-development-secret")

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS verified_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            headline TEXT NOT NULL,
            article TEXT NOT NULL,
            source TEXT NOT NULL,
            source_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        admin = con.execute("SELECT id FROM users WHERE username='admin'").fetchone()
        if not admin:
            con.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)",
                        ("admin", generate_password_hash("Admin@123"), "admin"))

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            flash("Admin access only.", "danger")
            return redirect(url_for("home"))
        return fn(*args, **kwargs)
    return wrapper

def normalize(text):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", text.lower())).strip()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if len(username) < 3 or len(password) < 6:
            flash("Username must be 3+ characters and password 6+ characters.", "danger")
        else:
            try:
                with db() as con:
                    con.execute("INSERT INTO users(username,password,role) VALUES(?,?,?)",
                                (username, generate_password_hash(password), "user"))
                flash("Account created. Please log in.", "success")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("That username already exists.", "danger")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with db() as con:
            user = con.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("admin") if user["role"] == "admin" else url_for("verify"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/admin", methods=["GET", "POST"])
@login_required
@admin_required
def admin():
    if request.method == "POST":
        headline = request.form.get("headline", "").strip()
        article = request.form.get("article", "").strip()
        source = request.form.get("source", "").strip()
        source_url = request.form.get("source_url", "").strip()
        if not all([headline, article, source]):
            flash("Headline, article and source are required.", "danger")
        else:
            with db() as con:
                con.execute("""INSERT INTO verified_news(headline,article,source,source_url)
                               VALUES(?,?,?,?)""", (headline, article, source, source_url))
            flash("Verified news record added.", "success")
            return redirect(url_for("admin"))
    with db() as con:
        news = con.execute("SELECT * FROM verified_news ORDER BY id DESC").fetchall()
    return render_template("admin.html", news=news)

@app.route("/admin/delete/<int:news_id>", methods=["POST"])
@login_required
@admin_required
def delete_news(news_id):
    with db() as con:
        con.execute("DELETE FROM verified_news WHERE id=?", (news_id,))
    flash("Record deleted.", "success")
    return redirect(url_for("admin"))

@app.route("/verify", methods=["GET", "POST"])
@login_required
def verify():
    result = None
    if request.method == "POST":
        text = request.form.get("news_text", "").strip()
        if len(text) < 20:
            flash("Please enter a longer news headline or article (at least 20 characters).", "warning")
        else:
            submitted = normalize(text)
            with db() as con:
                records = con.execute("SELECT * FROM verified_news").fetchall()
            match = None
            for item in records:
                known = normalize(item["headline"] + " " + item["article"])
                if submitted and (submitted in known or known in submitted):
                    match = item
                    break
            if match:
                result = {"status": "VERIFIED NEWS", "message": "This text matches a record entered by the administrator.",
                          "source": match["source"], "source_url": match["source_url"], "confidence": None}
            else:
                prediction = predict_news(text)
                if prediction is None:
                    result = {"status": "UNVERIFIED NEWS",
                              "message": "No admin-verified match was found and the ML model has not been trained yet.",
                              "source": None, "source_url": None, "confidence": None}
                elif prediction["label"] == "FAKE":
                    result = {"status": "LIKELY FAKE",
                              "message": "The ML model predicts that this text resembles fake-news examples. This is not proof.",
                              "source": None, "source_url": None, "confidence": prediction["confidence"]}
                else:
                    result = {"status": "UNVERIFIED NEWS",
                              "message": "The model predicts REAL, but this is not independent proof. No admin-verified match was found.",
                              "source": None, "source_url": None, "confidence": prediction["confidence"]}
    return render_template("verify.html", result=result)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

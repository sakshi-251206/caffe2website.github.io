from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os
from dotenv import load_dotenv

# ================= LOAD ENV =================
load_dotenv()

# ================= APP CONFIG =================
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

# ================= MYSQL CONNECTION =================
db = None
cursor = None

def init_db():
    global db, cursor
    try:
        db = mysql.connector.connect(
            host=os.getenv("MYSQLHOST"),
            user=os.getenv("MYSQLUSER"),
            password=os.getenv("MYSQLPASSWORD"),
            database=os.getenv("MYSQLDATABASE"),
            port=int(os.getenv("MYSQLPORT", 3306)),
            ssl_disabled=False
        )
        cursor = db.cursor(dictionary=True)
        print("Database connected successfully")
    except mysql.connector.Error as e:
        print("Database connection error:", e)
        db = None
        cursor = None

init_db()

# ================= ROUTES =================
@app.route("/")
def home():
    return render_template("index.html", user=session.get("user"))

@app.route("/contact", methods=["POST"])
def contact():
    if cursor is None:
        return "Database not connected"

    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    cursor.execute(
        "INSERT INTO contact_messages (name, email, message) VALUES (%s, %s, %s)",
        (name, email, message)
    )
    db.commit()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if cursor is None:
        return "Database not connected"

    if request.method == "POST":
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (
                request.form.get("username"),
                request.form.get("email"),
                request.form.get("password")
            )
        )
        db.commit()
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if cursor is None:
        return "Database not connected"

    if request.method == "POST":
        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (request.form.get("email"), request.form.get("password"))
        )
        user = cursor.fetchone()

        if user:
            session["user"] = user["username"]
            return redirect("/")
        else:
            return "Invalid Email or Password"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

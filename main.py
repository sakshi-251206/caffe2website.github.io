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
            ssl_disabled=True  # ⚠️ Use True for local/dev
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
    try:
        return render_template("index.html", user=session.get("user"))
    except Exception as e:
        return f"Template Error: {e}", 500

@app.route("/contact", methods=["POST"])
def contact():
    if cursor is None:
        return "Database not connected", 500

    try:
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")

        if not all([name, email, message]):
            return "All fields are required", 400

        cursor.execute(
            "INSERT INTO contact_messages (name, email, message) VALUES (%s, %s, %s)",
            (name, email, message)
        )
        db.commit()
        return redirect("/")
    except Exception as e:
        return f"Database Error: {e}", 500

@app.route("/register", methods=["GET", "POST"])
def register():
    if cursor is None:
        return "Database not connected", 500

    if request.method == "POST":
        try:
            username = request.form.get("username")
            email = request.form.get("email")
            password = request.form.get("password")

            if not all([username, email, password]):
                return "All fields are required", 400

            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, password)
            )
            db.commit()
            return redirect("/login")
        except mysql.connector.Error as e:
            return f"MySQL Error: {e}", 500

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if cursor is None:
        return "Database not connected", 500

    if request.method == "POST":
        try:
            email = request.form.get("email")
            password = request.form.get("password")

            cursor.execute(
                "SELECT * FROM users WHERE email=%s AND password=%s",
                (email, password)
            )
            user = cursor.fetchone()

            if user:
                session["user"] = user["username"]
                return redirect("/")
            else:
                return "Invalid Email or Password", 401
        except mysql.connector.Error as e:
            return f"MySQL Error: {e}", 500

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

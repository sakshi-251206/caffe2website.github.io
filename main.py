from flask import Flask, render_template, request, redirect, session
import mysql.connector
import os
from dotenv import load_dotenv

# ================= LOAD ENV =================
load_dotenv()

# ================= APP CONFIG =================
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# ================= MYSQL CONNECTION =================
db = None
cursor = None

def init_db():
    global db, cursor
    try:
        if db is None or not db.is_connected():
            db = mysql.connector.connect(
                host=os.getenv("MYSQLHOST"),
                user=os.getenv("MYSQLUSER"),
                password=os.getenv("MYSQLPASSWORD"),
                database=os.getenv("MYSQLDATABASE"),
                port=int(os.getenv("MYSQLPORT", 3306))
            )
            cursor = db.cursor(dictionary=True)
            print("Database connected successfully!")
    except mysql.connector.Error as e:
        print(f"DB Error: {e}")
        db = None
        cursor = None

init_db()

# ================= ROUTES =================
@app.route("/")
def home():
    return render_template("index.html", user=session.get("user"))

@app.route("/contact", methods=["POST"])
def contact():
    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]

    cursor.execute(
        "INSERT INTO contact_messages (name, email, message) VALUES (%s,%s,%s)",
        (name, email, message)
    )
    db.commit()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        cursor.execute(
            "INSERT INTO users (username,email,password) VALUES (%s,%s,%s)",
            (
                request.form["username"],
                request.form["email"],
                request.form["password"]
            )
        )
        db.commit()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (request.form["email"], request.form["password"])
        )
        user = cursor.fetchone()
        if user:
            session["user"] = user["username"]
            return redirect("/")
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

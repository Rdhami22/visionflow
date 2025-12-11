from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "visionflow_secret_key"


# -------------------------
# DATABASE CONNECTION
# -------------------------
def get_db():
    conn = sqlite3.connect("visionflow.db")
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------
# ENSURE DATABASE IS VALID
# -------------------------
def init_db():
    db = get_db()

    # Create users table if not exists
    db.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL,
        points INTEGER DEFAULT 0
    );
    """)

    # Ensure email column exists (fix for the no-column error)
    try:
        db.execute("SELECT email FROM users LIMIT 1;")
    except sqlite3.OperationalError:
        db.execute("ALTER TABLE users ADD COLUMN email TEXT;")

    # Create tasks table if not exists
    db.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        completed INTEGER DEFAULT 0
    );
    """)

    # Create rewards table if not exists
    db.execute("""
    CREATE TABLE IF NOT EXISTS rewards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        reward_text TEXT NOT NULL,
        date_claimed TEXT NOT NULL
    );
    """)

    db.commit()


# Run DB check once on startup
init_db()


# -------------------------
# AUTH CHECK
# -------------------------
def login_required(route):
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return route(*args, **kwargs)
    wrapper.__name__ = route.__name__
    return wrapper


# -------------------------
# HOME REDIRECT
# -------------------------
@app.route("/")
def home():
    return redirect("/dashboard")


# -------------------------
# SIGNUP
# -------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        db.execute("INSERT INTO users (username, email, password, points) VALUES (?, ?, ?, 0)",
                   (name, email, password))
        db.commit()
        return redirect("/login")

    return render_template("signup.html")


# -------------------------
# LOGIN
# -------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email=? AND password=?", 
                          (email, password)).fetchone()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/dashboard")
        else:
            return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# -------------------------
# DASHBOARD
# -------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()

    user = db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    tasks = db.execute("SELECT * FROM tasks WHERE user_id=?", (session["user_id"],)).fetchall()

    completed = db.execute("SELECT COUNT(*) as c FROM tasks WHERE user_id=? AND completed=1",
                           (session["user_id"],)).fetchone()["c"]
    total = db.execute("SELECT COUNT(*) as t FROM tasks WHERE user_id=?", 
                       (session["user_id"],)).fetchone()["t"]

    progress = int((completed / total) * 100) if total else 0

    return render_template("dashboard.html", user=user, tasks=tasks, progress=progress)


# -------------------------
# TASK ROUTES
# -------------------------
@app.route("/tasks")
@login_required
def tasks():
    db = get_db()
    tasks = db.execute("SELECT * FROM tasks WHERE user_id=?", (session["user_id"],)).fetchall()
    return render_template("tasks.html", tasks=tasks)


@app.route("/tasks/add", methods=["POST"])
@login_required
def add_task():
    title = request.form["title"]
    description = request.form["description"]

    db = get_db()
    db.execute("INSERT INTO tasks (user_id, title, description, completed) VALUES (?, ?, ?, 0)",
               (session["user_id"], title, description))
    db.commit()

    return redirect("/tasks")


@app.route("/tasks/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_task(id):
    db = get_db()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]

        db.execute("UPDATE tasks SET title=?, description=? WHERE id=? AND user_id=?",
                   (title, description, id, session["user_id"]))
        db.commit()
        return redirect("/tasks")

    task = db.execute("SELECT * FROM tasks WHERE id=? AND user_id=?", 
                      (id, session["user_id"])).fetchone()
    return render_template("edit_task.html", task=task)


@app.route("/tasks/delete/<int:id>")
@login_required
def delete_task(id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id=? AND user_id=?", (id, session["user_id"]))
    db.commit()
    return redirect("/tasks")


@app.route("/tasks/complete/<int:id>")
@login_required
def complete_task(id):
    db = get_db()
    db.execute("UPDATE tasks SET completed=1 WHERE id=? AND user_id=?", (id, session["user_id"]))
    db.execute("UPDATE users SET points = points + 1 WHERE id=?", (session["user_id"],))
    db.commit()
    return redirect("/tasks")


# -------------------------
# REWARDS
# -------------------------
@app.route("/rewards")
@login_required
def rewards():
    db = get_db()

    user = db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    rewards = db.execute("SELECT * FROM rewards WHERE user_id=? ORDER BY id DESC",
                         (session["user_id"],)).fetchall()

    progress_percent = min(user["points"], 100)

    return render_template("rewards.html", user=user, rewards=rewards, progress_percent=progress_percent)


@app.route("/rewards/claim", methods=["POST"])
@login_required
def claim_reward():
    db = get_db()

    user = db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()

    if user["points"] < 100:
        return redirect("/rewards")

    db.execute("INSERT INTO rewards (user_id, reward_text, date_claimed) VALUES (?, ?, ?)",
               (user["id"], "Reward Unlocked!", datetime.now().strftime("%Y-%m-%d")))
    db.execute("UPDATE users SET points = points - 100 WHERE id=?", (user["id"],))
    db.commit()

    return redirect("/rewards")


# -------------------------
# JOKES
# -------------------------
@app.route("/jokes")
@login_required
def jokes():
    jokes_list = [
        "Why did the student eat his homework? Because the teacher said it was a piece of cake!",
        "Parallel lines have so much in common. It’s a shame they’ll never meet.",
        "Why was the math book sad? It had too many problems.",
        "Why did the computer go to therapy? It had too many bugs."
    ]
    return render_template("jokes.html", jokes=jokes_list)


# -------------------------
# QUIZ
# -------------------------
@app.route("/quiz")
@login_required
def quiz():
    quizzes = [
        {"id": "philosophy", "name": "Philosophy", "icon": "🏛️", "count": 5},
        {"id": "literature", "name": "Literature", "icon": "📖", "count": 5},
        {"id": "history", "name": "History", "icon": "📜", "count": 5},
        {"id": "science", "name": "Science", "icon": "🔬", "count": 5},
        {"id": "computer", "name": "Computer Science", "icon": "💻", "count": 5},
    ]
    return render_template("quiz.html", quizzes=quizzes)


# -------------------------
# SETTINGS
# -------------------------
@app.route("/settings")
@login_required
def settings():
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    return render_template("settings.html", user=user)


# -------------------------
# RUN APP
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)

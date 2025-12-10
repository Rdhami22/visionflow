from flask import Flask, render_template, request, redirect, url_for, session, g, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "supersecretkey"
DATABASE = "visionflow.db"


# ================= DATABASE ================= #

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


def create_tables():
    db = get_db()
    cursor = db.cursor()

    # Users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        points INTEGER DEFAULT 0
                    )''')

    # Task table
    cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        task_name TEXT,
                        is_complete INTEGER DEFAULT 0,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )''')

    db.commit()


@app.before_request
def setup():
    create_tables()


@app.teardown_appcontext
def close_connection(exception=None):
    db = g.pop("db", None)
    if db:
        db.close()


# ================== LOGIN REQUIRED DECORATOR ================== #

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("You must login first")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


# ====================== ROUTES ====================== #

@app.route("/")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def do_login():
    username = request.form["username"]
    password = request.form["password"]

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if user and check_password_hash(user["password"], password):
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return redirect(url_for("dashboard"))

    flash("Invalid username or password")
    return redirect(url_for("login"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        try:
            db = get_db()
            db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            flash("Account created — Login now")
            return redirect(url_for("login"))
        except:
            flash("Username already exists")

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    points = db.execute("SELECT points FROM users WHERE id=?", (session["user_id"],)).fetchone()["points"]
    return render_template("dashboard.html", username=session["username"], points=points)


# ====================== TASK SYSTEM ====================== #

@app.route("/tasks")
@login_required
def tasks():
    db = get_db()
    tasks = db.execute("SELECT * FROM tasks WHERE user_id=?", (session["user_id"],)).fetchall()
    return render_template("tasks.html", tasks=tasks)


@app.route("/add_task", methods=["POST"])
@login_required
def add_task():
    db = get_db()
    db.execute("INSERT INTO tasks (user_id, task_name) VALUES (?, ?)", (session["user_id"], request.form["task"]))
    db.commit()
    return redirect(url_for("tasks"))


@app.route("/delete_task/<int:task_id>")
@login_required
def delete_task(task_id):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    db.commit()
    return redirect(url_for("tasks"))


@app.route("/complete_task/<int:task_id>")
@login_required
def complete_task(task_id):
    db = get_db()
    db.execute("UPDATE tasks SET is_complete=1 WHERE id=?", (task_id,))
    db.execute("UPDATE users SET points = points + 5 WHERE id=?", (session["user_id"],))
    db.commit()
    return redirect(url_for("tasks"))


@app.route("/edit_task/<int:task_id>")
@login_required
def edit_task(task_id):
    db = get_db()
    task = db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    return render_template("edit_task.html", task=task)


@app.route("/update_task/<int:task_id>", methods=["POST"])
@login_required
def update_task(task_id):
    db = get_db()
    db.execute("UPDATE tasks SET task_name=? WHERE id=?", (request.form["task_name"], task_id))
    db.commit()
    return redirect(url_for("tasks"))


# ====================== REWARDS ====================== #

@app.route("/rewards")
@login_required
def rewards():
    db = get_db()
    points = db.execute("SELECT points FROM users WHERE id=?", (session["user_id"],)).fetchone()["points"]
    return render_template("rewards.html", points=points)


# ====================== QUIZ + JOKES + SETTINGS ====================== #

@app.route("/quiz")
@login_required
def quiz():
    return render_template("quiz.html")


@app.route("/jokes")
@login_required
def jokes():
    return render_template("jokes.html")


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")


# ====================== RUN SERVER ====================== #

if __name__ == "__main__":
    with app.app_context():
        create_tables()
    app.run(debug=True)

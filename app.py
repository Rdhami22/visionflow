from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/tasks')
def tasks():
    return render_template('tasks.html')

@app.route('/rewards')
def rewards():
    return render_template('rewards.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

if __name__ == "__main__":
    app.run(debug=True)

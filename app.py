from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import sqlite3
from models.resume_parser import extract_text_from_resume
from models.job_matcher import calculate_match_score, recommend_jobs

app = Flask(__name__)
app.secret_key = 'resume_secret'
UPLOAD_FOLDER = 'uploads/resumes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Database Setup ---
def get_db_connection():
    conn = sqlite3.connect('database/users.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- Home ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Register ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, password))
        conn.commit()
        conn.close()
        flash("Registration successful!")
        return redirect(url_for('login'))
    return render_template('register.html')

# --- Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email=? AND password=?', (email, password)).fetchone()
        conn.close()
        if user:
            session['user'] = user['email']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

# --- Dashboard ---
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# --- Resume Upload ---
@app.route('/upload', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        file = request.files['resume']
        if file:
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(path)
            text = extract_text_from_resume(path)
            job_desc = request.form['job_description']
            match_score = calculate_match_score(text, job_desc)
            recommended_jobs = recommend_jobs(text)
            return render_template('result.html', score=match_score, jobs=recommended_jobs)
    return render_template('upload.html')

# --- Logout ---
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully!')
    return redirect(url_for('login'))

if __name__ == '__main__':
    if not os.path.exists('database/users.db'):
        os.makedirs('database', exist_ok=True)
        conn = get_db_connection()
        conn.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT)')
        conn.commit()
        conn.close()
    app.run(debug=True)

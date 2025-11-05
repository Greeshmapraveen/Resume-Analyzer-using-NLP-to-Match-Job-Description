import streamlit as st
import os
import sqlite3
from models.resume_parser import extract_text_from_resume
from models.job_matcher import calculate_match_score, recommend_jobs

# --- App Configuration ---
st.set_page_config(page_title="Resume Analyzer using NLP", page_icon="🧠", layout="wide")

# --- Custom Styling ---
st.markdown("""
    <style>
    .main-title {
        font-size: 35px;
        font-weight: bold;
        color: #2E86C1;
        text-align: center;
        margin-bottom: 10px;
    }
    .sub-title {
        text-align: center;
        color: #117A65;
        font-size: 18px;
        margin-bottom: 30px;
    }
    .result-box {
        background-color: #F8F9F9;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 0px 8px #D5D8DC;
    }
    </style>
""", unsafe_allow_html=True)

# --- Database Setup ---
def get_db_connection():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect('database/users.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT)')
    conn.commit()
    return conn

# --- App Header ---
st.markdown('<p class="main-title">🧠 Resume Analyzer using NLP</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Match your resume with job descriptions using AI-powered NLP</p>', unsafe_allow_html=True)

# --- Sidebar Navigation ---
menu = ["🏠 Home", "📝 Register", "🔐 Login", "📊 Dashboard", "📄 Upload Resume"]
choice = st.sidebar.radio("Navigation", menu)

# --- Home Page ---
if choice == "🏠 Home":
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=150)
    st.write("""
    ### 👋 Welcome!
    This tool analyzes your resume and matches it with job descriptions using advanced **Natural Language Processing (NLP)**.
    - Upload your resume.
    - Paste the job description.
    - Get your **match score** and **recommended jobs** instantly!
    """)

# --- Register Page ---
elif choice == "📝 Register":
    st.subheader("🆕 Create a New Account")
    with st.form("register_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Register")

    if submit:
        conn = get_db_connection()
        conn.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, password))
        conn.commit()
        conn.close()
        st.success("🎉 Registration successful! You can now login.")

# --- Login Page ---
elif choice == "🔐 Login":
    st.subheader("Login to Your Account")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email=? AND password=?', (email, password)).fetchone()
        conn.close()

        if user:
            st.session_state["user"] = email
            st.success(f"✅ Welcome, {email}!")
        else:
            st.error("❌ Invalid credentials. Please try again.")

# --- Dashboard ---
elif choice == "📊 Dashboard":
    if "user" in st.session_state:
        st.success(f"👋 Hello, {st.session_state['user']}!")
        st.info("Navigate to 'Upload Resume' in the sidebar to analyze your resume.")
    else:
        st.warning("⚠️ Please login first.")

# --- Upload Resume Page ---
elif choice == "📄 Upload Resume":
    if "user" not in st.session_state:
        st.warning("⚠️ Please login first.")
    else:
        st.subheader("📄 Upload Your Resume & Match with Job Description")

        job_desc = st.text_area("🧾 Enter the Job Description")
        uploaded_file = st.file_uploader("📎 Upload Resume", type=["pdf", "docx"])

        if uploaded_file and job_desc:
            os.makedirs("uploads/resumes", exist_ok=True)
            resume_path = os.path.join("uploads/resumes", uploaded_file.name)
            with open(resume_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Extract text and calculate match
            text = extract_text_from_resume(resume_path)
            match_score = calculate_match_score(text, job_desc)
            recommended_jobs = recommend_jobs(text)

            # Display results
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### ✅ Match Result:")
            st.progress(int(match_score))
            st.info(f"**Match Score:** {match_score:.2f}%")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 💼 Recommended Jobs:")
            with st.container():
                for job in recommended_jobs:
                    st.markdown(f"- 🔹 {job}")

# --- Logout ---
if "user" in st.session_state:
    if st.sidebar.button("🚪 Logout"):
        del st.session_state["user"]
        st.info("You have been logged out successfully.")

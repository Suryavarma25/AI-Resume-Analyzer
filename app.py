import os
import sqlite3

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

from werkzeug.utils import secure_filename

import fitz


app = Flask(__name__)

app.secret_key = "ai-resume-analyzer-secret-key"


# ==================================================
# DATABASE
# ==================================================

DATABASE_FOLDER = "database"
DATABASE_PATH = os.path.join(
    DATABASE_FOLDER,
    "users.db"
)

os.makedirs(
    DATABASE_FOLDER,
    exist_ok=True
)


# ==================================================
# UPLOAD SETTINGS
# ==================================================

UPLOAD_FOLDER = "uploads"

ALLOWED_EXTENSIONS = {
    "pdf"
}

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ==================================================
# CREATE DATABASE
# ==================================================

def create_database():

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL

        )
    """)

    connection.commit()

    connection.close()


create_database()


# ==================================================
# CHECK FILE
# ==================================================

def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ==================================================
# HOME
# ==================================================

@app.route("/")
def home():

    return redirect(
        url_for("login")
    )


# ==================================================
# REGISTER
# ==================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "GET":

        return render_template(
            "register.html"
        )

    name = request.form.get(
        "name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    password = request.form.get(
        "password",
        ""
    )

    confirm_password = request.form.get(
        "confirm_password",
        ""
    )


    if not name:

        return render_template(
            "register.html",
            error="Please enter your name."
        )


    if not email:

        return render_template(
            "register.html",
            error="Please enter your email."
        )


    if len(password) < 6:

        return render_template(
            "register.html",
            error="Password must contain at least 6 characters."
        )


    if password != confirm_password:

        return render_template(
            "register.html",
            error="Passwords do not match."
        )


    try:

        connection = sqlite3.connect(
            DATABASE_PATH
        )

        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password)

            VALUES (?, ?, ?)
            """,
            (
                name,
                email,
                password
            )
        )

        connection.commit()

        connection.close()


    except sqlite3.IntegrityError:

        return render_template(
            "register.html",
            error="This email is already registered."
        )


    return render_template(
        "register.html",
        success="Registration successful. Please login."
    )


# ==================================================
# LOGIN
# ==================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "GET":

        return render_template(
            "login.html"
        )


    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    password = request.form.get(
        "password",
        ""
    )


    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT id, name, email
        FROM users
        WHERE email = ?
        AND password = ?
        """,
        (
            email,
            password
        )
    )


    user = cursor.fetchone()

    connection.close()


    if user is None:

        return render_template(
            "login.html",
            error="Invalid email or password."
        )


    session["user_id"] = user[0]
    session["user_name"] = user[1]
    session["user_email"] = user[2]


    return redirect(
        url_for("dashboard")
    )


# ==================================================
# DASHBOARD
# ==================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    return render_template(
        "dashboard.html",
        name=session["user_name"],
        email=session["user_email"]
    )


# ==================================================
# UPLOAD PAGE
# ==================================================

@app.route(
    "/upload",
    methods=["GET"]
)
def upload():

    # User must login first

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    return render_template(
        "upload.html"
    )


# ==================================================
# ANALYZE RESUME
# ==================================================

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    # Check file

    if "resume" not in request.files:

        return render_template(
            "upload.html",
            error="Please select a resume."
        )


    file = request.files["resume"]


    if file.filename == "":

        return render_template(
            "upload.html",
            error="Please select a PDF file."
        )


    if not allowed_file(file.filename):

        return render_template(
            "upload.html",
            error="Only PDF files are allowed."
        )


    # ==================================================
    # SAVE PDF
    # ==================================================

    filename = secure_filename(
        file.filename
    )


    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )


    file.save(file_path)


    # ==================================================
    # READ PDF
    # ==================================================

    try:

        document = fitz.open(
            file_path
        )

        text = ""


        for page in document:

            text += page.get_text()


        document.close()


    except Exception as error:

        return render_template(
            "upload.html",
            error=f"Could not read PDF: {error}"
        )


    # ==================================================
    # BASIC ATS ANALYSIS
    # ==================================================

    text_lower = text.lower()


    score = 0

    strengths = []

    mistakes = []

    suggestions = []

    implementations = []


    # ----------------------------------------------
    # CONTACT INFORMATION
    # ----------------------------------------------

    contact_keywords = [
        "email",
        "@",
        "phone",
        "mobile",
        "linkedin",
        "github"
    ]


    contact_count = sum(
        1
        for keyword in contact_keywords
        if keyword in text_lower
    )


    if contact_count >= 3:

        score += 15

        strengths.append(
            "Contact information is present."
        )

    else:

        mistakes.append(
            "Important contact information may be missing."
        )

        suggestions.append(
            "Add email, phone number, LinkedIn and GitHub."
        )

        implementations.append(
            "Create a clear contact section at the top of your resume."
        )


    # ----------------------------------------------
    # EDUCATION
    # ----------------------------------------------

    if "education" in text_lower:

        score += 10

        strengths.append(
            "Education section detected."
        )

    else:

        mistakes.append(
            "Education section was not detected."
        )

        suggestions.append(
            "Add a clearly named Education section."
        )

        implementations.append(
            "Use the heading 'Education' and list your degree, college and graduation year."
        )


    # ----------------------------------------------
    # EXPERIENCE
    # ----------------------------------------------

    experience_words = [
        "experience",
        "internship",
        "intern",
        "work experience"
    ]


    if any(
        word in text_lower
        for word in experience_words
    ):

        score += 15

        strengths.append(
            "Experience or internship section detected."
        )

    else:

        mistakes.append(
            "Experience section was not detected."
        )

        suggestions.append(
            "Add internships, training or relevant experience."
        )

        implementations.append(
            "Describe your internship using action + task + result."
        )


    # ----------------------------------------------
    # PROJECTS
    # ----------------------------------------------

    if "project" in text_lower:

        score += 15

        strengths.append(
            "Projects section detected."
        )

    else:

        mistakes.append(
            "Projects section was not detected."
        )

        suggestions.append(
            "Add 2-3 relevant technical projects."
        )

        implementations.append(
            "Add project title, technologies used and measurable results."
        )


    # ----------------------------------------------
    # SKILLS
    # ----------------------------------------------

    skill_keywords = [
        "python",
        "sql",
        "excel",
        "power bi",
        "java",
        "javascript",
        "html",
        "css",
        "pandas",
        "numpy",
        "git"
    ]


    detected_skills = [
        skill
        for skill in skill_keywords
        if skill in text_lower
    ]


    if len(detected_skills) >= 4:

        score += 20

        strengths.append(
            "Good number of technical skills detected."
        )

    else:

        mistakes.append(
            "Technical skills section appears weak."
        )

        suggestions.append(
            "Add relevant technical skills based on your target job."
        )

        implementations.append(
            "Create a dedicated Skills section containing job-relevant technologies."
        )


    # ----------------------------------------------
    # KEYWORDS
    # ----------------------------------------------

    if len(text.split()) >= 250:

        score += 10

        strengths.append(
            "Resume contains sufficient content for keyword analysis."
        )

    else:

        mistakes.append(
            "Resume appears to contain limited content."
        )

        suggestions.append(
            "Add more relevant achievements, projects and technical keywords."
        )

        implementations.append(
            "Use job descriptions to identify missing keywords."
        )


    # ----------------------------------------------
    # FORMATTING
    # ----------------------------------------------

    if len(text.split()) <= 900:

        score += 10

    else:

        mistakes.append(
            "Resume may contain too much content."
        )

        suggestions.append(
            "Keep the resume concise and preferably one page for fresher roles."
        )

        implementations.append(
            "Remove repetitive descriptions and unnecessary personal information."
        )


    # Maximum score

    if score > 100:

        score = 100


    # ==================================================
    # SCORE LEVEL
    # ==================================================

    if score >= 80:

        score_message = "Excellent ATS readiness"

    elif score >= 65:

        score_message = "Good ATS readiness"

    elif score >= 50:

        score_message = "Needs improvement"

    else:

        score_message = "Low ATS readiness"


    # ==================================================
    # HOW TO INCREASE SCORE
    # ==================================================

    improvement_tips = [

        "Match your resume keywords with the target job description.",

        "Use standard section headings such as Summary, Skills, Experience, Projects and Education.",

        "Use simple ATS-friendly formatting.",

        "Add measurable achievements wherever possible.",

        "Remove unnecessary graphics, tables and excessive formatting.",

        "Keep important technical skills clearly visible.",

        "Customize your resume for every important job application."

    ]


    # ==================================================
    # RESULTS
    # ==================================================

    return render_template(
        "results.html",

        score=score,

        score_message=score_message,

        strengths=strengths,

        mistakes=mistakes,

        suggestions=suggestions,

        implementations=implementations,

        improvement_tips=improvement_tips,

        detected_skills=detected_skills,

        filename=filename
    )


# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )
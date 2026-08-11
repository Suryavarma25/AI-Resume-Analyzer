import re


SKILLS = [
    "python",
    "java",
    "javascript",
    "html",
    "css",
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "excel",
    "power bi",
    "tableau",
    "pandas",
    "numpy",
    "scikit-learn",
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "flask",
    "django",
    "react",
    "git",
    "github",
    "aws",
    "azure",
    "docker",
    "linux",
    "data analysis",
    "data visualization",
    "powerpoint",
]


def analyze_resume(text):

    text_lower = text.lower()

    # ==========================================
    # 1. WORD COUNT
    # ==========================================

    words = text.split()
    word_count = len(words)


    # ==========================================
    # 2. FIND SKILLS
    # ==========================================

    found_skills = []

    for skill in SKILLS:

        if skill in text_lower:

            found_skills.append(skill.title())


    # ==========================================
    # 3. CHECK RESUME SECTIONS
    # ==========================================

    sections = {

        "Contact Information": [
            "email",
            "phone",
            "mobile",
            "linkedin"
        ],

        "Professional Summary": [
            "summary",
            "profile",
            "objective"
        ],

        "Education": [
            "education",
            "b.tech",
            "bachelor",
            "degree"
        ],

        "Experience": [
            "experience",
            "internship",
            "work experience"
        ],

        "Projects": [
            "projects",
            "project"
        ],

        "Skills": [
            "skills",
            "technical skills"
        ],

        "Certifications": [
            "certification",
            "certifications",
            "certificate"
        ]
    }


    section_results = {}

    for section, keywords in sections.items():

        found = any(
            keyword in text_lower
            for keyword in keywords
        )

        section_results[section] = found


    # ==========================================
    # 4. CATEGORY SCORES
    # ==========================================

    category_scores = {}


    # Skills score
    skill_score = min(
        len(found_skills) * 3,
        25
    )

    category_scores["Skills"] = skill_score


    # Sections score
    section_score = round(
        (sum(section_results.values()) /
         len(section_results)) * 20
    )

    category_scores["Sections"] = section_score


    # Contact score
    contact_score = 0

    if re.search(
        r"[\w\.-]+@[\w\.-]+\.\w+",
        text
    ):
        contact_score += 5

    if re.search(
        r"\+?\d[\d\s\-]{8,}",
        text
    ):
        contact_score += 5

    if "linkedin.com" in text_lower:
        contact_score += 5

    category_scores["Contact"] = contact_score


    # Content score
    content_score = 0

    if word_count >= 300:
        content_score += 10

    elif word_count >= 150:
        content_score += 6

    elif word_count >= 80:
        content_score += 3

    if "responsible" not in text_lower:
        content_score += 0

    category_scores["Content"] = content_score


    # ==========================================
    # 5. ATS KEYWORD SCORE
    # ==========================================

    keyword_score = min(
        len(found_skills) * 2,
        15
    )

    category_scores["Keywords"] = keyword_score


    # ==========================================
    # 6. TOTAL ATS SCORE
    # ==========================================

    score = sum(category_scores.values())

    score = min(score, 100)


    # ==========================================
    # 7. MISTAKES
    # ==========================================

    mistakes = []


    if word_count < 150:

        mistakes.append(
            {
                "title": "Resume content is too short",
                "description":
                "Your resume contains very little text. "
                "Important skills, projects and achievements may be missing.",
                "severity": "High"
            }
        )


    if len(found_skills) < 5:

        mistakes.append(
            {
                "title": "Too few technical skills detected",
                "description":
                "The ATS may not find enough keywords related "
                "to the job you are applying for.",
                "severity": "High"
            }
        )


    if not section_results["Professional Summary"]:

        mistakes.append(
            {
                "title": "Professional summary is missing",
                "description":
                "A short targeted summary can help recruiters "
                "understand your profile quickly.",
                "severity": "Medium"
            }
        )


    if not section_results["Projects"]:

        mistakes.append(
            {
                "title": "Projects section is missing",
                "description":
                "Projects are important for freshers because "
                "they demonstrate practical skills.",
                "severity": "High"
            }
        )


    if not section_results["Experience"]:

        mistakes.append(
            {
                "title": "Experience or internship section is missing",
                "description":
                "Add internships, training, freelance work, "
                "or relevant practical experience if applicable.",
                "severity": "Medium"
            }
        )


    if not section_results["Certifications"]:

        mistakes.append(
            {
                "title": "Certifications are missing",
                "description":
                "Relevant certifications can strengthen your "
                "technical profile.",
                "severity": "Low"
            }
        )


    if not re.search(
        r"[\w\.-]+@[\w\.-]+\.\w+",
        text
    ):

        mistakes.append(
            {
                "title": "Email address not detected",
                "description":
                "Your email address could not be detected "
                "from the extracted resume text.",
                "severity": "High"
            }
        )


    if "linkedin.com" not in text_lower:

        mistakes.append(
            {
                "title": "LinkedIn profile not detected",
                "description":
                "A professional LinkedIn profile can improve "
                "your recruiter visibility.",
                "severity": "Medium"
            }
        )


    # ==========================================
    # 8. MISSING SECTIONS
    # ==========================================

    missing_sections = [

        section

        for section, found
        in section_results.items()

        if not found
    ]


    # ==========================================
    # 9. SUGGESTIONS
    # ==========================================

    suggestions = []


    if len(found_skills) < 5:

        suggestions.append(
            {
                "title": "Add job-relevant technical skills",

                "description":
                "Add skills that actually appear in the "
                "job description.",

                "implementation":
                "Create a Skills section containing relevant "
                "skills such as Python, SQL, Excel, Power BI, "
                "Pandas or other skills required by the target job.",

                "impact": "+5 to +15 points"
            }
        )


    if not section_results["Professional Summary"]:

        suggestions.append(
            {
                "title": "Add a professional summary",

                "description":
                "Create a 2-4 line summary targeted toward "
                "your desired role.",

                "implementation":
                "Example: 'Final-year B.Tech student with skills "
                "in Python, SQL, Excel and Power BI, seeking an "
                "entry-level Data Analyst role.'",

                "impact": "+3 to +5 points"
            }
        )


    if not section_results["Projects"]:

        suggestions.append(
            {
                "title": "Add strong projects",

                "description":
                "Projects demonstrate practical experience, "
                "especially for freshers.",

                "implementation":
                "Add 2-3 projects. For each project mention "
                "the problem, technologies used, your contribution "
                "and measurable result.",

                "impact": "+5 to +10 points"
            }
        )


    if not section_results["Experience"]:

        suggestions.append(
            {
                "title": "Add practical experience",

                "description":
                "Internships and practical training can improve "
                "your resume credibility.",

                "implementation":
                "Add relevant internships, virtual internships, "
                "freelance projects or practical training with "
                "2-4 achievement-focused bullet points.",

                "impact": "+3 to +8 points"
            }
        )


    if not section_results["Certifications"]:

        suggestions.append(
            {
                "title": "Add relevant certifications",

                "description":
                "Relevant certifications can support your skills.",

                "implementation":
                "Add certifications related to your target role. "
                "Include certification name and issuing organization.",

                "impact": "+2 to +5 points"
            }
        )


    if word_count < 150:

        suggestions.append(
            {
                "title": "Add more useful resume content",

                "description":
                "Your resume is too short.",

                "implementation":
                "Add measurable project achievements, "
                "technical skills, education details and "
                "relevant experience.",

                "impact": "+5 to +10 points"
            }
        )


    # ==========================================
    # 10. GENERAL ATS RULES
    # ==========================================

    general_tips = [

        "Use standard section headings such as Skills, Education, Experience and Projects.",

        "Use simple ATS-friendly formatting instead of complex tables or graphics.",

        "Use keywords from the job description naturally throughout the resume.",

        "Use measurable achievements such as percentages, numbers or time saved.",

        "Avoid unnecessary personal information.",

        "Keep the resume concise and relevant to the target role.",

        "Use a professional PDF file with selectable text."
    ]


    # ==========================================
    # 11. SCORE LEVEL
    # ==========================================

    if score >= 80:

        score_level = "Excellent"

    elif score >= 65:

        score_level = "Good"

    elif score >= 50:

        score_level = "Needs Improvement"

    else:

        score_level = "Low"


    # ==========================================
    # 12. RETURN RESULTS
    # ==========================================

    return {

        "score": score,

        "score_level": score_level,

        "skills": found_skills,

        "sections": section_results,

        "missing_sections": missing_sections,

        "mistakes": mistakes,

        "suggestions": suggestions,

        "general_tips": general_tips,

        "category_scores": category_scores,

        "word_count": word_count
    }
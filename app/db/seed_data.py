import os
import uuid
from pathlib import Path
from datetime import datetime
import docx
from app.config import SAMPLE_DIR
from app.db.client import db_manager

def generate_sample_docx(path: Path, name: str, title: str, exp: str, edu: str, skills: list, experience_text: str):
    """Creates a realistic formatted DOCX resume for test uploads."""
    doc = docx.Document()
    
    # Header
    doc.add_heading(name, level=0)
    p_meta = doc.add_paragraph()
    p_meta.add_run(f"Role: {title} | Education: {edu} | Total Experience: {exp}\n")
    p_meta.add_run(f"Email: {name.lower().replace(' ', '.')}@example.com | Phone: +91 9876543210")
    
    # Profile Summary
    doc.add_heading("Professional Summary", level=1)
    doc.add_paragraph(
        f"Dynamic and results-driven {title} with {exp} of professional experience. "
        f"Proficient in designing scalable architectures, optimizing backend logic, and solving complex technical challenges."
    )
    
    # Skills
    doc.add_heading("Technical Proficiencies", level=1)
    doc.add_paragraph(", ".join(skills))
    
    # Work Experience
    doc.add_heading("Work History", level=1)
    doc.add_paragraph(experience_text)
    
    # Education
    doc.add_heading("Education", level=1)
    doc.add_paragraph(f"{edu} in Computer Science - Graduated with Distinction.")
    
    doc.save(str(path))

def generate_sample_txt(path: Path, name: str, title: str, exp: str, edu: str, skills: list, experience_text: str):
    """Creates a formatted text resume."""
    content = f"""{name}
{title}
Email: {name.lower().replace(' ', '.')}@example.com | Phone: +91 9123456780
Total Experience: {exp}
Education: {edu}

SUMMARY:
Motivated {title} with {exp} in software engineering and production systems.

TECHNICAL SKILLS:
{', '.join(skills)}

WORK EXPERIENCE:
{experience_text}

EDUCATION:
{edu} - First Class with Honors
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def generate_sample_pdf(path: Path, name: str, title: str, exp: str, edu: str, skills: list, experience_text: str):
    """Generates a valid raw PDF 1.4 resume file using pure Python."""
    lines = [
        f"{name}",
        f"Role: {title} - Experience: {exp}",
        f"Email: {name.lower().replace(' ', '.')}@example.com - Phone: 9876543210",
        f"Education: {edu}",
        "---",
        "SKILLS:",
        f"{', '.join(skills[:8])}",
        f"{', '.join(skills[8:]) if len(skills) > 8 else ''}",
        "---",
        "EXPERIENCE:",
        f"{experience_text[:120]}",
        f"{experience_text[120:240]}",
        "EDUCATION:",
        f"{edu} in Computer Science"
    ]
    
    # Build PDF stream
    text_ops = []
    y = 750
    for line in lines:
        if not line:
            continue
        safe_line = line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        text_ops.append(f"1 0 0 1 50 {y} Tm ({safe_line}) Tj")
        y -= 22
        
    stream_content = f"BT /F1 11 Tf {' '.join(text_ops)} ET"
    stream_len = len(stream_content.encode('latin1'))

    pdf_text = f"""%PDF-1.4
1 0 obj <</Type /Catalog /Pages 2 0 R>> endobj
2 0 obj <</Type /Pages /Kids [3 0 R] /Count 1>> endobj
3 0 obj <</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources <</Font <</F1 5 0 R>>>>>> endobj
4 0 obj <</Length {stream_len}>> stream
{stream_content}
endstream
endobj
5 0 obj <</Type /Font /Subtype /Type1 /BaseFont /Helvetica>> endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000244 00000 n 
0000000325 00000 n 
trailer <</Size 6 /Root 1 0 R>>
startxref
400
%%EOF"""
    with open(path, "wb") as f:
        f.write(pdf_text.encode('latin1'))

def seed_database():
    """Initializes sample jobs, candidates, user, and generates sample files."""
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Seed User
    if not db_manager.users.find_one({"username": "lipika"}):
        db_manager.users.insert_one({
            "id": "lipika-admin-01",
            "username": "lipika",
            "password": "admin123",
            "name": "Lipika Murmu",
            "role": "Lead Technical Recruiter",
            "department": "Human Resources",
            "email": "lipika.murmu@lipikaai.com",
            "created_at": "2026-09-20 09:00"
        })
        print("[Seed] Seeded Lipika Murmu admin user.")
        
    if not db_manager.users.find_one({"username": "admin"}):
        db_manager.users.insert_one({
            "id": "system-admin-01",
            "username": "admin",
            "password": "admin123",
            "name": "Lipika Murmu",
            "role": "System Administrator",
            "department": "Human Resources",
            "email": "admin@lipikaai.com",
            "created_at": "2026-09-20 09:00"
        })
        print("[Seed] Seeded primary admin user.")

    # 2. Seed Jobs
    jobs_data = [
        {
            "id": "job-python-01",
            "title": "Senior Python / FastAPI Developer",
            "department": "Backend Engineering",
            "required_skills": ["Python", "FastAPI", "Django", "REST API", "SQL", "Docker"],
            "preferred_skills": ["AWS", "Redis", "PostgreSQL", "Microservices"],
            "min_experience": 2.5,
            "education_level": "Bachelor",
            "description": "Looking for an experienced Python developer to build robust async REST APIs using FastAPI and Django. Responsible for designing clean database schemas in SQL and PostgreSQL, containerizing apps with Docker, and architecting microservices with Redis caching and AWS deployment.",
            "status": "Active",
            "created_at": "2026-09-20 10:00"
        },
        {
            "id": "job-ml-02",
            "title": "AI & Machine Learning Engineer",
            "department": "AI & Data Science",
            "required_skills": ["Python", "Machine Learning", "Natural Language Processing (NLP)", "PyTorch", "Scikit-Learn", "Pandas"],
            "preferred_skills": ["HuggingFace", "Deep Learning", "Docker", "Large Language Models (LLMs)"],
            "min_experience": 2.0,
            "education_level": "Master",
            "description": "Seeking an AI/ML Engineer to train semantic embeddings, develop document parsing and resume screening NLP models, and deploy high-throughput inference endpoints using PyTorch, Scikit-Learn, and HuggingFace transformers.",
            "status": "Active",
            "created_at": "2026-09-22 11:30"
        },
        {
            "id": "job-fullstack-03",
            "title": "Full Stack MERN Developer",
            "department": "Product Engineering",
            "required_skills": ["React", "Node.js", "Express.js", "JavaScript", "MongoDB", "HTML", "CSS"],
            "preferred_skills": ["TypeScript", "Next.js", "Tailwind CSS", "REST API"],
            "min_experience": 3.0,
            "education_level": "Bachelor",
            "description": "We are seeking a talented Full Stack Web Developer proficient in React, Node.js, Express.js, and MongoDB to create dynamic, high-performance dashboards, real-time collaboration tools, and responsive interfaces.",
            "status": "Active",
            "created_at": "2026-09-24 14:15"
        },
        {
            "id": "job-devops-04",
            "title": "Cloud & DevOps Specialist",
            "department": "Infrastructure",
            "required_skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Terraform"],
            "preferred_skills": ["Python", "Git", "Nginx", "Jenkins"],
            "min_experience": 3.0,
            "education_level": "Bachelor",
            "description": "Responsible for managing cloud infrastructure on AWS, building automated CI/CD pipelines, orchestrating containerized microservices on Kubernetes, and provisioning infrastructure as code using Terraform.",
            "status": "Active",
            "created_at": "2026-09-25 09:00"
        }
    ]

    for j in jobs_data:
        if not db_manager.jobs.find_one({"id": j["id"]}):
            db_manager.jobs.insert_one(j)
    print(f"[Seed] Seeded {len(jobs_data)} jobs.")

    # 3. Seed Sample Resumes & Candidates
    candidates_data = [
        {
            "id": "cand-01",
            "name": "Rahul Sharma",
            "email": "rahul.sharma@example.com",
            "phone": "+91 9876543210",
            "skills": ["Python", "FastAPI", "Django", "REST API", "SQL", "PostgreSQL", "Docker", "Redis", "Git", "AWS"],
            "experience_years": 3.4,
            "education": "MCA",
            "summary": "Rahul Sharma is a candidate with MCA and 3.4 years of experience. Key proficiencies include: Python, FastAPI, Django, REST API, SQL.",
            "raw_text": """Rahul Sharma
Senior Python Developer
Email: rahul.sharma@example.com | Phone: +91 9876543210
Total Experience: 3.4 years | Education: MCA in Computer Applications

PROFESSIONAL SUMMARY:
Backend Developer with 3.4 years of experience developing high-performance REST APIs with Python, FastAPI, and Django. Skilled in PostgreSQL, SQL, Docker containerization, Redis caching, and AWS deployment.

TECHNICAL SKILLS:
Python, FastAPI, Django, REST API, SQL, PostgreSQL, Docker, Redis, Git, AWS, Microservices

WORK EXPERIENCE:
• Lead Backend Developer at TechNova Solutions (2022 - Present)
- Engineered scalable async REST APIs with FastAPI and Django serving 200k daily requests.
- Designed database schemas in PostgreSQL and SQL with optimized query execution.
- Deployed microservices using Docker containers on AWS EC2 and configured Redis caching layer.

• Software Engineer at CloudCraft Systems (2020 - 2022)
- Built internal tooling and RESTful APIs using Python, SQL, and Flask.

EDUCATION:
Master of Computer Applications (MCA) - Pune University (2018 - 2020)
""",
            "resume_filename": "Rahul_Sharma_Resume.pdf",
            "resume_path": str(SAMPLE_DIR / "Rahul_Sharma_Resume.pdf"),
            "uploaded_at": "2026-09-25 15:30",
            "status": "Shortlisted"
        },
        {
            "id": "cand-02",
            "name": "Priya Patel",
            "email": "priya.patel@example.com",
            "phone": "+91 9876501234",
            "skills": ["Python", "Machine Learning", "Natural Language Processing (NLP)", "PyTorch", "Scikit-Learn", "Pandas", "NumPy", "Deep Learning", "HuggingFace", "Git"],
            "experience_years": 2.8,
            "education": "M.Tech",
            "summary": "Priya Patel is an AI Engineer with M.Tech and 2.8 years of experience in NLP and ML models.",
            "raw_text": """Priya Patel
AI & Machine Learning Engineer
Email: priya.patel@example.com | Phone: +91 9876501234
Experience: 2.8 years | Education: M.Tech in Data Science

SUMMARY:
Machine Learning Engineer with 2.8 years of experience building Natural Language Processing models, document classification pipelines, and transformer architectures.

TECHNICAL SKILLS:
Python, Machine Learning, Natural Language Processing (NLP), PyTorch, Scikit-Learn, Pandas, NumPy, Deep Learning, HuggingFace, Git

WORK EXPERIENCE:
• ML Research Engineer at AI Nexus Labs (2023 - Present)
- Fine-tuned transformer models using HuggingFace and PyTorch for semantic text similarity.
- Built automated resume entity extraction pipelines with NLP and Scikit-Learn classifiers.

• Junior Data Scientist at DataPulse (2021 - 2023)
- Processed large datasets using Pandas and NumPy, implemented ML algorithms for predictive modeling.

EDUCATION:
M.Tech in Data Science and Artificial Intelligence (2019 - 2021)
""",
            "resume_filename": "Priya_Patel_Resume.docx",
            "resume_path": str(SAMPLE_DIR / "Priya_Patel_Resume.docx"),
            "uploaded_at": "2026-09-25 16:10",
            "status": "Shortlisted"
        },
        {
            "id": "cand-03",
            "name": "Amit Verma",
            "email": "amit.verma@example.com",
            "phone": "+91 9988776655",
            "skills": ["React", "JavaScript", "Node.js", "Express.js", "MongoDB", "HTML", "CSS", "Tailwind CSS", "Git", "REST API"],
            "experience_years": 4.1,
            "education": "B.Tech / B.E.",
            "summary": "Amit Verma is a Full Stack Developer with 4.1 years of experience in MERN stack.",
            "raw_text": """Amit Verma
Full Stack MERN Developer
Email: amit.verma@example.com | Phone: +91 9988776655
Experience: 4.1 years of experience | Education: B.Tech in Computer Science

SUMMARY:
Experienced Full Stack Engineer with 4.1 years building dynamic web applications using React, Node.js, Express.js, and MongoDB.

TECHNICAL SKILLS:
React, Node.js, Express.js, JavaScript, MongoDB, HTML, CSS, Tailwind CSS, Git, REST API

WORK EXPERIENCE:
• Senior Full Stack Developer at WebSphere Innovations (2022 - Present)
- Architected responsive dashboards in React and Tailwind CSS.
- Developed backend microservices using Node.js, Express.js, and MongoDB.

• Full Stack Developer at DevSolutions (2019 - 2022)
- Implemented state management, user authentication, and interactive client components.

EDUCATION:
Bachelor of Technology (B.Tech) in Computer Science (2015 - 2019)
""",
            "resume_filename": "Amit_Verma_Resume.docx",
            "resume_path": str(SAMPLE_DIR / "Amit_Verma_Resume.docx"),
            "uploaded_at": "2026-09-26 10:20",
            "status": "Active"
        },
        {
            "id": "cand-04",
            "name": "Neha Singh",
            "email": "neha.singh@example.com",
            "phone": "+91 9711223344",
            "skills": ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Terraform", "Git", "Jenkins", "Python"],
            "experience_years": 3.5,
            "education": "B.Tech / B.E.",
            "summary": "Neha Singh is a DevOps Specialist with B.Tech and 3.5 years of cloud experience.",
            "raw_text": """Neha Singh
Cloud & DevOps Engineer
Email: neha.singh@example.com | Phone: +91 9711223344
Experience: 3.5 years | Education: B.Tech in Information Technology

SUMMARY:
DevOps Engineer with 3.5 years hands-on experience provisioning AWS cloud resources, building CI/CD pipelines, and managing Docker and Kubernetes clusters.

TECHNICAL SKILLS:
Docker, Kubernetes, AWS, CI/CD, Linux, Terraform, Git, Jenkins, Python

WORK EXPERIENCE:
• DevOps Engineer at CloudMatrix (2022 - Present)
- Built automated Git-driven CI/CD pipelines with Jenkins and GitHub Actions.
- Managed Kubernetes production clusters on AWS EKS and automated infra with Terraform.

• Systems Engineer at InfraTech (2020 - 2022)
- Maintained Linux server fleets, containerized legacy services with Docker.

EDUCATION:
B.Tech in Information Technology (2016 - 2020)
""",
            "resume_filename": "Neha_Singh_Resume.pdf",
            "resume_path": str(SAMPLE_DIR / "Neha_Singh_Resume.pdf"),
            "uploaded_at": "2026-09-26 11:45",
            "status": "Active"
        },
        {
            "id": "cand-05",
            "name": "Vikram Rao",
            "email": "vikram.rao@example.com",
            "phone": "+91 9655443322",
            "skills": ["Python", "Django", "SQL", "HTML", "CSS", "Git"],
            "experience_years": 1.2,
            "education": "BCA",
            "summary": "Vikram Rao is a Junior Python Developer with BCA and 1.2 years of experience.",
            "raw_text": """Vikram Rao
Junior Python Developer
Email: vikram.rao@example.com | Phone: +91 9655443322
Experience: 1.2 years | Education: BCA

SUMMARY:
Motivated Junior Python Developer with 1.2 years experience developing web features with Django and SQL.

TECHNICAL SKILLS:
Python, Django, SQL, HTML, CSS, Git

WORK EXPERIENCE:
• Junior Web Developer at ByteLogic (2023 - Present)
- Assisted in building Django views, models, and SQL queries.

EDUCATION:
Bachelor of Computer Applications (BCA) - 2023
""",
            "resume_filename": "Vikram_Rao_Resume.txt",
            "resume_path": str(SAMPLE_DIR / "Vikram_Rao_Resume.txt"),
            "uploaded_at": "2026-09-26 14:00",
            "status": "Active"
        },
        {
            "id": "cand-06",
            "name": "Ananya Sen",
            "email": "ananya.sen@example.com",
            "phone": "+91 9544332211",
            "skills": ["React", "JavaScript", "TypeScript", "Next.js", "HTML", "CSS", "Tailwind CSS", "Vue.js", "Git"],
            "experience_years": 2.5,
            "education": "B.Sc / B.S.",
            "summary": "Ananya Sen is a Frontend Engineer with B.Sc and 2.5 years of experience in React and TypeScript.",
            "raw_text": """Ananya Sen
Frontend Specialist
Email: ananya.sen@example.com | Phone: +91 9544332211
Experience: 2.5 years | Education: B.Sc in Computer Science

SUMMARY:
Frontend Engineer with 2.5 years experience crafting responsive modern user interfaces with React, Next.js, and TypeScript.

TECHNICAL SKILLS:
React, JavaScript, TypeScript, Next.js, HTML, CSS, Tailwind CSS, Vue.js, Git

WORK EXPERIENCE:
• Frontend Developer at PixelCraft Studios (2022 - Present)
- Built interactive web portals and reusable component libraries using React and TypeScript.

EDUCATION:
Bachelor of Science (B.Sc) in Computer Science (2019 - 2022)
""",
            "resume_filename": "Ananya_Sen_Resume.pdf",
            "resume_path": str(SAMPLE_DIR / "Ananya_Sen_Resume.pdf"),
            "uploaded_at": "2026-09-26 15:30",
            "status": "Active"
        }
    ]

    for c in candidates_data:
        if not db_manager.candidates.find_one({"id": c["id"]}):
            db_manager.candidates.insert_one(c)
    print(f"[Seed] Seeded {len(candidates_data)} candidates.")

    # 4. Generate real sample files on disk in data/sample_resumes/
    try:
        generate_sample_pdf(
            SAMPLE_DIR / "Rahul_Sharma_Resume.pdf",
            "Rahul Sharma", "Senior Python Developer", "3.4 years", "MCA",
            ["Python", "FastAPI", "Django", "REST API", "SQL", "PostgreSQL", "Docker", "Redis", "AWS"],
            "Engineered scalable async REST APIs with FastAPI and Django. Deployed microservices using Docker on AWS EC2."
        )
        generate_sample_docx(
            SAMPLE_DIR / "Priya_Patel_Resume.docx",
            "Priya Patel", "AI & Machine Learning Engineer", "2.8 years", "M.Tech",
            ["Python", "Machine Learning", "NLP", "PyTorch", "Scikit-Learn", "Pandas", "HuggingFace"],
            "Fine-tuned transformer models for semantic text similarity. Built resume entity extraction pipelines with NLP."
        )
        generate_sample_docx(
            SAMPLE_DIR / "Amit_Verma_Resume.docx",
            "Amit Verma", "Full Stack MERN Developer", "4.1 years", "B.Tech",
            ["React", "JavaScript", "Node.js", "Express.js", "MongoDB", "HTML", "CSS", "Tailwind CSS"],
            "Architected responsive dashboards in React and Tailwind CSS. Developed backend microservices using Node.js and MongoDB."
        )
        generate_sample_pdf(
            SAMPLE_DIR / "Neha_Singh_Resume.pdf",
            "Neha Singh", "Cloud & DevOps Engineer", "3.5 years", "B.Tech",
            ["Docker", "Kubernetes", "AWS", "CI/CD", "Linux", "Terraform", "Git", "Jenkins"],
            "Built automated Git-driven CI/CD pipelines. Managed Kubernetes production clusters on AWS EKS with Terraform."
        )
        generate_sample_txt(
            SAMPLE_DIR / "Vikram_Rao_Resume.txt",
            "Vikram Rao", "Junior Python Developer", "1.2 years", "BCA",
            ["Python", "Django", "SQL", "HTML", "CSS", "Git"],
            "Assisted in building Django views, models, and SQL queries with Python."
        )
        print(f"[Seed] Successfully created physical sample resume files in {SAMPLE_DIR}")
    except Exception as e:
        print(f"[Seed] Warning generating sample documents: {e}")

if __name__ == "__main__":
    seed_database()

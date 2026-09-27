import re
from typing import List, Dict, Any, Optional, Set
from datetime import datetime

class NLPExtractorService:
    """Natural Language Processing service for entity, skill, experience, and education extraction."""

    def __init__(self):
        self._init_skills_database()
        self._init_education_database()

    def _init_skills_database(self):
        # Comprehensive tech skills mapping: canonical name -> list of aliases/patterns
        self.skills_taxonomy: Dict[str, List[str]] = {
            # Programming Languages
            "Python": ["python", "python3", "py"],
            "JavaScript": ["javascript", "js", "ecmascript"],
            "TypeScript": ["typescript", "ts"],
            "Java": ["java", "core java", "j2ee"],
            "C++": ["c++", "cpp"],
            "C#": ["c#", "csharp", ".net c#"],
            "C": ["c language", "ansi c"],
            "Go": ["golang", "go language"],
            "Rust": ["rust", "rustlang"],
            "Ruby": ["ruby"],
            "PHP": ["php", "php7", "php8"],
            "Swift": ["swift", "swiftui"],
            "Kotlin": ["kotlin", "android kotlin"],
            "Dart": ["dart"],
            "SQL": ["sql", "t-sql", "pl/sql", "ansi sql"],
            "R": ["r programming", "r language"],
            "Scala": ["scala"],
            "HTML": ["html", "html5"],
            "CSS": ["css", "css3", "sass", "scss", "less"],

            # Frameworks & Libraries
            "FastAPI": ["fastapi", "fast-api"],
            "Django": ["django", "django rest framework", "drf"],
            "Flask": ["flask"],
            "React": ["react", "react.js", "reactjs"],
            "Node.js": ["node.js", "nodejs", "node"],
            "Express.js": ["express", "express.js", "expressjs"],
            "Next.js": ["next.js", "nextjs"],
            "Vue.js": ["vue", "vue.js", "vuejs"],
            "Angular": ["angular", "angularjs", "angular 2+"],
            "Spring Boot": ["spring boot", "springboot", "spring framework"],
            "ASP.NET": ["asp.net", "asp.net core", ".net core"],
            "Laravel": ["laravel"],
            "Ruby on Rails": ["rails", "ruby on rails"],
            "Tailwind CSS": ["tailwind", "tailwind css", "tailwindcss"],
            "Bootstrap": ["bootstrap", "bootstrap 5"],
            "jQuery": ["jquery"],

            # Databases & Caches
            "MongoDB": ["mongodb", "mongo", "nosql mongodb"],
            "PostgreSQL": ["postgresql", "postgres", "psql"],
            "MySQL": ["mysql"],
            "Redis": ["redis"],
            "SQLite": ["sqlite", "sqlite3"],
            "Oracle Database": ["oracle", "oracle db"],
            "Cassandra": ["cassandra", "apache cassandra"],
            "Elasticsearch": ["elasticsearch", "elastic search", "elk"],
            "DynamoDB": ["dynamodb", "aws dynamodb"],
            "Firebase": ["firebase", "firestore"],

            # Cloud & DevOps
            "AWS": ["aws", "amazon web services", "ec2", "s3", "lambda"],
            "Docker": ["docker", "containerization"],
            "Kubernetes": ["kubernetes", "k8s"],
            "Azure": ["azure", "microsoft azure"],
            "GCP": ["gcp", "google cloud", "google cloud platform"],
            "Terraform": ["terraform"],
            "CI/CD": ["ci/cd", "ci-cd", "continuous integration", "continuous deployment"],
            "Jenkins": ["jenkins"],
            "GitHub Actions": ["github actions", "gh actions"],
            "Git": ["git", "github", "gitlab", "bitbucket"],
            "Linux": ["linux", "ubuntu", "centos", "debian", "bash"],
            "Nginx": ["nginx"],
            "Ansible": ["ansible"],

            # Machine Learning & AI
            "Machine Learning": ["machine learning", "ml"],
            "Deep Learning": ["deep learning", "dl"],
            "Natural Language Processing (NLP)": ["nlp", "natural language processing"],
            "Computer Vision": ["computer vision", "cv", "opencv"],
            "PyTorch": ["pytorch"],
            "TensorFlow": ["tensorflow", "tf"],
            "Scikit-Learn": ["scikit-learn", "sklearn"],
            "Pandas": ["pandas"],
            "NumPy": ["numpy"],
            "Keras": ["keras"],
            "HuggingFace": ["huggingface", "transformers"],
            "Large Language Models (LLMs)": ["llm", "llms", "large language models", "gpt"],
            "LangChain": ["langchain"],
            "NLTK": ["nltk"],
            "spaCy": ["spacy"],

            # Architecture & Engineering Practices
            "REST API": ["rest api", "restful api", "restful apis", "rest apis", "rest"],
            "GraphQL": ["graphql"],
            "Microservices": ["microservices", "microservice architecture"],
            "System Design": ["system design", "distributed systems"],
            "Agile": ["agile", "scrum", "kanban"],
            "Unit Testing": ["unit testing", "pytest", "jest", "junit", "tdd", "test driven development"],
            "Object-Oriented Programming": ["oop", "object-oriented programming", "oops"]
        }

    def _init_education_database(self):
        # Degrees ranking and matching patterns
        self.degrees_map = [
            ("Ph.D", 5, [r"\bph\.?d\b", r"\bdoctorate\b", r"\bdoctor of philosophy\b"]),
            ("M.Tech", 4, [r"\bm\.?tech\b", r"\bmaster of technology\b"]),
            ("MCA", 4, [r"\bmca\b", r"\bmaster of computer applications\b"]),
            ("M.Sc / M.S", 4, [r"\bm\.?sc\b", r"\bm\.?s\b", r"\bmaster of science\b"]),
            ("MBA", 4, [r"\bmba\b", r"\bmaster of business administration\b"]),
            ("B.Tech / B.E.", 3, [r"\bb\.?tech\b", r"\bb\.?e\b", r"\bbachelor of technology\b", r"\bbachelor of engineering\b"]),
            ("BCA", 3, [r"\bbca\b", r"\bbachelor of computer applications\b"]),
            ("B.Sc / B.S.", 3, [r"\bb\.?sc\b", r"\bb\.?s\b", r"\bbachelor of science\b"]),
            ("B.Com / BBA", 3, [r"\bb\.?com\b", r"\bbba\b", r"\bbachelor of commerce\b"]),
            ("Diploma", 2, [r"\bdiploma\b", r"\bpolytechnic\b"]),
            ("High School", 1, [r"\b12th\b", r"\bhigher secondary\b", r"\bhigh school\b"])
        ]

    def extract_email(self, text: str) -> Optional[str]:
        """Extracts email address using standard RFC pattern."""
        pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        match = re.search(pattern, text)
        return match.group(0).lower() if match else ""

    def extract_phone(self, text: str) -> Optional[str]:
        """Extracts phone number with support for international and local formats."""
        patterns = [
            r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', # Standard US / Intl
            r'(\+91[-.\s]?)?[6-9]\d{9}',                                  # Indian 10-digit mobile
            r'\b\d{10}\b'                                                # Clean 10 digits
        ]
        for p in patterns:
            match = re.search(p, text)
            if match:
                phone = match.group(0).strip()
                # Ensure it's not a year or zip code
                digits = re.sub(r'\D', '', phone)
                if len(digits) >= 10:
                    return phone
        return ""

    def extract_name(self, text: str, email: str = "") -> str:
        """Extracts candidate name using top-section line analysis and entity heuristics."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Stop words that indicate headers rather than names
        header_blacklist = {
            "curriculum vitae", "resume", "cv", "profile", "contact", 
            "summary", "objective", "experience", "education", "skills",
            "personal details", "projects", "certifications", "about me"
        }
        
        for line in lines[:6]:  # Look inside the first few lines
            clean_line = re.sub(r'[^a-zA-Z\s]', '', line).strip()
            lower_line = clean_line.lower()
            
            # Check length: names are typically 2 to 4 words, 4 to 35 characters
            words = clean_line.split()
            if 2 <= len(words) <= 4 and 4 <= len(clean_line) <= 35:
                if not any(header in lower_line for header in header_blacklist):
                    # Check if title case or all caps
                    if all(w[0].isupper() for w in words if w):
                        return clean_line.title()
                    elif line.isupper():
                        return clean_line.title()

        # Fallback to email username if available
        if email:
            prefix = email.split('@')[0]
            clean_prefix = re.sub(r'[\d._-]+', ' ', prefix).strip()
            if len(clean_prefix) >= 3:
                return clean_prefix.title()

        return "Candidate"

    def extract_skills(self, text: str) -> List[str]:
        """Extracts technical skills by scanning text against canonical taxonomy."""
        text_lower = text.lower()
        extracted: Set[str] = set()

        for canonical_name, aliases in self.skills_taxonomy.items():
            for alias in aliases:
                # Handle special characters in alias like c++, c#, .net
                escaped = re.escape(alias)
                # Word boundary check: for single-letter words or special symbols, enforce clean boundaries
                if len(alias) <= 2 and not any(c in alias for c in ['+', '#']):
                    pattern = rf'(?<![a-zA-Z0-9]){escaped}(?![a-zA-Z0-9])'
                else:
                    pattern = rf'\b{escaped}\b'
                    if any(c in alias for c in ['+', '#', '.']):
                        pattern = rf'(?<![a-zA-Z0-9]){escaped}(?![a-zA-Z0-9])'
                
                if re.search(pattern, text_lower):
                    extracted.add(canonical_name)
                    break

        return sorted(list(extracted))

    def extract_experience_years(self, text: str) -> float:
        """Calculates experience in years via numerical statements and employment date spans."""
        years = 0.0

        # Pattern 1: Direct statement (e.g. "3.5 years of experience", "5+ yrs experience")
        direct_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)(?:\s+of)?\s+(?:experience|exp)',
            r'(?:experience|exp)\s*:\s*(\d+(?:\.\d+)?)\s*(?:\+)?\s*(?:years?|yrs?)',
            r'worked\s+for\s+(\d+(?:\.\d+)?)\s*(?:years?|yrs?)',
            r'total\s+experience\s*:\s*(\d+(?:\.\d+)?)\s*(?:years?|yrs?)'
        ]
        
        for p in direct_patterns:
            matches = re.findall(p, text, re.IGNORECASE)
            for m in matches:
                try:
                    val = float(m)
                    if 0.5 <= val <= 40.0 and val > years:
                        years = val
                except ValueError:
                    pass

        if years > 0:
            return round(years, 1)

        # Pattern 2: Date ranges in work experience section (e.g. 2019 - 2023 or 2021 to Present)
        current_year = datetime.now().year
        date_range_pattern = r'\b(20\d{2}|19\d{2})\s*(?:-|–|to)\s*(20\d{2}|present|current)\b'
        matches = re.findall(date_range_pattern, text, re.IGNORECASE)
        
        calculated_span = 0.0
        for start_str, end_str in matches:
            try:
                start = int(start_str)
                end = current_year if end_str.lower() in ["present", "current"] else int(end_str)
                if end >= start and (end - start) <= 30:
                    span = max(1.0, float(end - start))
                    calculated_span += span
            except ValueError:
                pass

        if calculated_span > 0:
            return round(min(calculated_span, 35.0), 1)

        return 0.0

    def extract_education(self, text: str) -> Dict[str, Any]:
        """Detects highest educational degree achieved."""
        text_lower = text.lower()
        
        for deg_name, level, patterns in self.degrees_map:
            for p in patterns:
                if re.search(p, text_lower):
                    return {
                        "degree": deg_name,
                        "level": level,
                        "matched_text": deg_name
                    }
                    
        return {
            "degree": "Graduate / Not Specified",
            "level": 2,
            "matched_text": "Not Specified"
        }

    def generate_candidate_summary(self, name: str, skills: List[str], experience: float, education: str) -> str:
        """Generates a concise HR profile summary from extracted attributes."""
        exp_desc = f"{experience} years of experience" if experience > 0 else "Entry-level / Fresher"
        top_skills = ", ".join(skills[:5]) if skills else "General technical skills"
        return f"{name} is a candidate with {education} and {exp_desc}. Key proficiencies include: {top_skills}."

    def extract_profile(self, text: str, filename: str = "") -> Dict[str, Any]:
        """Extracts complete candidate profile from raw document text."""
        email = self.extract_email(text)
        phone = self.extract_phone(text)
        name = self.extract_name(text, email=email)
        skills = self.extract_skills(text)
        experience_years = self.extract_experience_years(text)
        edu_info = self.extract_education(text)
        summary = self.generate_candidate_summary(name, skills, experience_years, edu_info["degree"])

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "skills": skills,
            "experience_years": experience_years,
            "education": edu_info["degree"],
            "education_level": edu_info["level"],
            "summary": summary,
            "raw_text": text,
            "resume_filename": filename
        }

nlp_extractor = NLPExtractorService()

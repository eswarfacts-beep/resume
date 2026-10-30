"""
TalentIQ AI - Skills Extraction & Normalization Engine
Comprehensive tech, cloud, AI, and soft skills ontology with precise regex boundaries.
"""

import re
from typing import Dict, List, Set, Any

# Canonical skill taxonomy grouped by category
SKILL_TAXONOMY: Dict[str, List[str]] = {
    "programming_languages": [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "C", "Go", "Golang",
        "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "Dart", "Julia",
        "Perl", "Haskell", "Elixir", "Lua", "Shell", "Bash", "PowerShell", "SQL", "HTML", "CSS"
    ],
    "frameworks_libraries": [
        "React", "React.js", "Angular", "Vue.js", "Vue", "Next.js", "Nuxt.js", "Svelte",
        "Node.js", "Express.js", "Express", "Django", "FastAPI", "Flask", "Spring Boot", "Spring",
        ".NET", ".NET Core", "ASP.NET", "Ruby on Rails", "Laravel", "NestJS", "Fastify",
        "PyTorch", "TensorFlow", "Keras", "Scikit-Learn", "Pandas", "NumPy", "SciPy",
        "OpenCV", "Hugging Face", "Transformers", "LangChain", "LlamaIndex", "Tailwind CSS",
        "Bootstrap", "Material UI", "Redux", "GraphQL", "REST API", "gRPC"
    ],
    "cloud_devops": [
        "AWS", "Amazon Web Services", "Microsoft Azure", "Azure", "Google Cloud", "GCP",
        "Docker", "Kubernetes", "K8s", "Terraform", "Ansible", "Helm", "Jenkins", "GitHub Actions",
        "GitLab CI", "CircleCI", "ArgoCD", "Prometheus", "Grafana", "Datadog", "CloudWatch",
        "Nginx", "Apache", "Linux", "Unix", "Ubuntu", "Serverless", "Lambda", "OpenShift"
    ],
    "databases": [
        "PostgreSQL", "Postgres", "MySQL", "MongoDB", "Redis", "Elasticsearch", "Cassandra",
        "DynamoDB", "SQLite", "Oracle", "Microsoft SQL Server", "MSSQL", "Snowflake",
        "BigQuery", "Redshift", "Neo4j", "Firebase", "Supabase", "MariaDB", "CouchDB", "Milvus", "ChromaDB", "Pinecone"
    ],
    "ai_ml_data": [
        "Machine Learning", "Deep Learning", "Artificial Intelligence", "Natural Language Processing",
        "NLP", "Computer Vision", "Large Language Models", "LLMs", "Generative AI", "GenAI",
        "RAG", "Retrieval Augmented Generation", "Data Engineering", "Data Science", "ETL",
        "Apache Spark", "Spark", "Apache Kafka", "Kafka", "Airflow", "Hadoop", "Tableau",
        "Power BI", "Fine-Tuning", "Prompt Engineering", "Vector Embeddings", "Neural Networks"
    ],
    "tools_platforms": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence", "Postman", "Swagger",
        "VS Code", "IntelliJ", "Figma", "Docker Compose", "Webpack", "Vite", "Linux CLI"
    ],
    "soft_skills": [
        "Problem Solving", "Critical Thinking", "Communication", "Leadership", "Team Collaboration",
        "Agile Methodology", "Scrum", "Mentorship", "Adaptability", "Time Management",
        "Cross-functional Leadership", "Analytical Skills", "Stakeholder Management"
    ]
}

# Skill synonyms & canonical mappings
SKILL_ALIASES: Dict[str, str] = {
    "golang": "Go",
    "react.js": "React",
    "reactjs": "React",
    "vue.js": "Vue",
    "vuejs": "Vue",
    "nextjs": "Next.js",
    "node": "Node.js",
    "nodejs": "Node.js",
    "expressjs": "Express",
    "express.js": "Express",
    "k8s": "Kubernetes",
    "amazon web services": "AWS",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "microsoft azure": "Azure",
    "postgres": "PostgreSQL",
    "mssql": "Microsoft SQL Server",
    "genai": "Generative AI",
    "llm": "LLMs",
    "llms": "LLMs",
    "scikit learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "spring-boot": "Spring Boot",
    "net core": ".NET Core",
    "dot net": ".NET",
    "git hub": "GitHub"
}


def build_skill_pattern(skill: str) -> re.Pattern:
    """Creates a boundary-safe regex pattern for a skill string."""
    escaped = re.escape(skill)
    # Special handling for C++, C#, .NET where standard \b fails on punctuation
    if skill.lower() in ["c++", "c#", ".net", "c"]:
        if skill.lower() == "c++":
            return re.compile(r"(?<![a-zA-Z0-9])C\+\+(?![a-zA-Z0-9])", re.IGNORECASE)
        elif skill.lower() == "c#":
            return re.compile(r"(?<![a-zA-Z0-9])C#(?![a-zA-Z0-9])", re.IGNORECASE)
        elif skill.lower() == ".net":
            return re.compile(r"(?<![a-zA-Z0-9])\.NET(?![a-zA-Z0-9])", re.IGNORECASE)
        elif skill.lower() == "c":
            return re.compile(r"(?<![a-zA-Z0-9])C(?![a-zA-Z0-9\+#])", re.IGNORECASE)
        elif skill.lower() == "r":
            return re.compile(r"(?<![a-zA-Z0-9])R(?![a-zA-Z0-9])", re.IGNORECASE)
    return re.compile(rf"(?<![\w\-]){escaped}(?![\w\-])", re.IGNORECASE)


# Precompile pattern registry
_COMPILED_PATTERNS = {}
for category, skills in SKILL_TAXONOMY.items():
    for skill in skills:
        _COMPILED_PATTERNS[skill] = (build_skill_pattern(skill), category)


def normalize_skill_name(skill: str) -> str:
    """Converts a skill name to its canonical casing and name."""
    s_clean = skill.strip()
    low = s_clean.lower()
    if low in SKILL_ALIASES:
        return SKILL_ALIASES[low]
    # Check taxonomy matches
    for skills in SKILL_TAXONOMY.values():
        for sk in skills:
            if sk.lower() == low:
                return sk
    return s_clean.title()


def extract_skills(text: str) -> Dict[str, Any]:
    """
    Extracts all recognized skills from given text with category breakdown.
    Returns categorized dictionary and flat unique list.
    """
    if not text:
        return {
            "all_skills": [],
            "skills_by_category": {},
            "total_count": 0,
            "category_counts": {}
        }

    detected_skills: Set[str] = set()
    category_map: Dict[str, List[str]] = {cat: [] for cat in SKILL_TAXONOMY}

    for skill_name, (pattern, cat) in _COMPILED_PATTERNS.items():
        if pattern.search(text):
            canonical = normalize_skill_name(skill_name)
            if canonical not in detected_skills:
                detected_skills.add(canonical)
                if cat in category_map and canonical not in category_map[cat]:
                    category_map[cat].append(canonical)

    # Sort each category list alphabetically
    for cat in category_map:
        category_map[cat].sort()

    all_skills_sorted = sorted(list(detected_skills))
    category_counts = {cat: len(skills) for cat, skills in category_map.items() if len(skills) > 0}

    return {
        "all_skills": all_skills_sorted,
        "skills_by_category": category_map,
        "total_count": len(detected_skills),
        "category_counts": category_counts
    }


def get_skill_category(skill_name: str) -> str:
    """Returns the primary category identifier for a skill."""
    canonical = normalize_skill_name(skill_name)
    for cat, skills in SKILL_TAXONOMY.items():
        for sk in skills:
            if normalize_skill_name(sk).lower() == canonical.lower():
                if cat in ["cloud_devops"]:
                    return "cloud"
                elif cat in ["ai_ml_data"]:
                    return "ai"
                elif cat in ["soft_skills"]:
                    return "soft"
                else:
                    return "tech"
    return "tech"


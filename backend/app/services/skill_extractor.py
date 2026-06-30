"""Skill and evidence vocabulary used by the ranking pipeline."""

import re
from functools import lru_cache


_NON_TERM_RE = re.compile(r"[^a-z0-9+#.]+")
_WHITESPACE_RE = re.compile(r"\s+")


@lru_cache(maxsize=4096)
def _clean_term(value: str) -> str:
    """Normalize punctuation/spacing before taxonomy lookup."""
    value = (value or "").lower()
    value = value.replace("&", " and ")
    value = _NON_TERM_RE.sub(" ", value)
    return _WHITESPACE_RE.sub(" ", value).strip()


SKILL_TAXONOMY = {
    "Machine Learning": [
        "machine learning",
        "ml",
    ],
    "Natural Language Processing": [
        "natural language processing",
        "nlp",
    ],
    "Computer Vision": [
        "computer vision",
        "cv",
    ],
    "Hugging Face": [
        "hugging face",
        "hf",
        "hugging face transformers",
    ],
    "Large Language Model": [
        "large language model",
        "large language models",
        "llm",
        "llms",
    ],
    "Tensor Flow": [
        "tensor flow",
        "tensorflow",
    ],
    "Torch": [
        "torch",
        "pytorch",
    ],
    "Recommender Systems": [
        "recommender systems",
        "recommendation systems",
        "recommendation engine",
        "recommendation engines",
    ],
    "Python": ["python"],
    "Deep Learning": ["deep learning"],
    "Transformers": ["transformers"],
    "MLOps": ["mlops", "ml ops"],
    "SQL": ["sql"],
    "Spark": ["spark", "apache spark", "pyspark"],
    "Embeddings": ["embeddings", "embedding"],
    "FAISS": ["faiss"],
    "Vector Search": ["vector search", "semantic search"],
    "Vector Database": [
        "vector database",
        "vector databases",
        "vector db",
        "vector dbs",
        "milvus",
        "pinecone",
        "weaviate",
        "chromadb",
    ],
    "Fine Tuning": [
        "fine tuning",
        "fine tune",
        "fine tuned",
        "fine tuning llms",
        "fine tuning large language models",
    ],
    "Sentence Transformers": ["sentence transformers", "sentence transformer"],
    "Elasticsearch": ["elasticsearch", "elastic search"],
    "OpenSearch": ["opensearch", "open search"],
    "Information Retrieval": ["information retrieval", "retrieval"],
    "LoRA": ["lora", "low rank adaptation"],
    "LangChain": ["langchain", "lang chain"],
    "RAG": [
        "rag",
        "retrieval augmented generation",
        "retrieval augmentation",
    ],
    "Inference": ["inference", "model serving", "serving"],
    "Kubernetes": ["kubernetes", "k8s"],
    "CI/CD": ["ci cd", "cicd", "continuous integration", "continuous delivery"],
}

SKILL_ALIASES = {
    _clean_term(alias): canonical
    for canonical, aliases in SKILL_TAXONOMY.items()
    for alias in aliases
}

# Relevant skills weighted by duration and endorsements.
RELEVANT_SKILLS = list(SKILL_TAXONOMY.keys())
RELEVANT_SKILL_SET = set(RELEVANT_SKILLS)

# Reasoning-only tiers. These improve which skills are surfaced to recruiters
# without changing the scoring taxonomy above.
CORE_REASONING_SKILLS = {
    "Python",
    "Machine Learning",
    "Deep Learning",
    "Statistics",
    "SQL",
    "Git",
    "Linux",
}

DIFFERENTIATOR_REASONING_SKILLS = {
    "LLMs",
    "RAG",
    "Pinecone",
    "Weaviate",
    "Milvus",
    "FAISS",
    "Vector Search",
    "Embeddings",
    "Sentence Transformers",
    "Hugging Face",
    "LoRA",
    "QLoRA",
    "LangChain",
    "OpenSearch",
    "Elasticsearch",
    "MLflow",
    "Kubeflow",
    "Docker",
    "Kubernetes",
    "CI/CD",
    "TensorRT",
    "ONNX",
}

REASONING_SKILL_ALIASES = {
    "python": "Python",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "deep learning": "Deep Learning",
    "statistics": "Statistics",
    "sql": "SQL",
    "git": "Git",
    "linux": "Linux",
    "large language model": "LLMs",
    "large language models": "LLMs",
    "llm": "LLMs",
    "llms": "LLMs",
    "rag": "RAG",
    "retrieval augmented generation": "RAG",
    "retrieval augmentation": "RAG",
    "pinecone": "Pinecone",
    "weaviate": "Weaviate",
    "milvus": "Milvus",
    "faiss": "FAISS",
    "vector search": "Vector Search",
    "semantic search": "Vector Search",
    "embeddings": "Embeddings",
    "embedding": "Embeddings",
    "sentence transformers": "Sentence Transformers",
    "sentence transformer": "Sentence Transformers",
    "hugging face": "Hugging Face",
    "hf": "Hugging Face",
    "hugging face transformers": "Hugging Face",
    "lora": "LoRA",
    "low rank adaptation": "LoRA",
    "qlora": "QLoRA",
    "langchain": "LangChain",
    "lang chain": "LangChain",
    "opensearch": "OpenSearch",
    "open search": "OpenSearch",
    "elasticsearch": "Elasticsearch",
    "elastic search": "Elasticsearch",
    "mlflow": "MLflow",
    "kubeflow": "Kubeflow",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "ci cd": "CI/CD",
    "cicd": "CI/CD",
    "continuous integration": "CI/CD",
    "continuous delivery": "CI/CD",
    "tensorrt": "TensorRT",
    "onnx": "ONNX",
}

REASONING_SKILL_ALIAS_PATTERNS = [
    (
        re.compile(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])"),
        display_name,
    )
    for alias, display_name in REASONING_SKILL_ALIASES.items()
]

CAREER_EVIDENCE_GROUPS = {
    "build": ["built", "build", "developed", "designed", "implemented", "created"],
    "deployment": [
        "deployed",
        "deployment",
        "model deployment",
        "model deployments",
        "production",
        "production ml",
        "launched",
        "shipped",
        "release",
    ],
    "scale": ["scaled", "scaling", "latency", "throughput", "users", "performance"],
    "operations": [
        "monitoring",
        "model monitoring",
        "observability",
        "mlops",
        "ci cd",
        "cicd",
        "kubernetes",
        "k8s",
        "docker",
        "containerized",
        "containers",
    ],
    "data_pipeline": [
        "pipeline",
        "pipelines",
        "etl",
        "streaming",
        "spark",
        "feature store",
        "feature stores",
        "feast",
    ],
    "ai_systems": [
        "rag",
        "vector database",
        "vector databases",
        "llm",
        "llms",
        "large language model",
        "inference",
        "retrieval",
        "embeddings",
    ],
}

PRODUCTION_TERMS = [
    term
    for terms in CAREER_EVIDENCE_GROUPS.values()
    for term in terms
]

STRONG_TITLES = [
    "ai engineer", "ml engineer", "machine learning engineer",
    "research scientist", "applied scientist"
]

MEDIUM_TITLES = [
    "data scientist", "ai", "ml", "machine learning"
]

ROLE_JD_PROFILES = [
    {
        "keywords": ("llm", "large language model", "generative ai", "genai"),
        "strong_titles": ("llm engineer", "large language model engineer", "ai engineer"),
        "medium_titles": ("llm", "large language model", "generative ai", "ai"),
        "skills": (
            "Large Language Model", "RAG", "LangChain", "Vector Search",
            "Embeddings", "Hugging Face", "Fine Tuning", "LoRA",
            "Inference", "Python",
        ),
        "career_terms": (
            "llm", "llms", "large language model", "rag", "retrieval",
            "embeddings", "vector search", "fine tuning", "inference",
            "prompt", "prompts", "model serving",
        ),
    },
    {
        "keywords": ("nlp", "natural language", "text analytics"),
        "strong_titles": ("nlp engineer", "natural language processing engineer", "machine learning engineer"),
        "medium_titles": ("nlp", "natural language processing", "machine learning", "text"),
        "skills": (
            "Natural Language Processing", "Transformers", "Hugging Face",
            "Sentence Transformers", "Python", "Machine Learning",
            "Deep Learning",
        ),
        "career_terms": (
            "nlp", "natural language", "text", "transformers", "hugging face",
            "sentence transformer", "language model", "tokenization",
            "classification", "information extraction",
        ),
    },
    {
        "keywords": ("data scientist", "data science", "analytics scientist"),
        "strong_titles": ("data scientist", "senior data scientist", "applied scientist"),
        "medium_titles": ("data science", "analytics", "machine learning", "statistics", "modeling"),
        "skills": (
            "Python", "SQL", "Machine Learning", "Statistics",
            "Spark", "Feature Engineering", "Experimentation",
        ),
        "career_terms": (
            "data science", "statistics", "statistical", "experiment",
            "experimentation", "modeling", "predictive", "analytics",
            "feature engineering", "sql", "dashboard", "metrics",
        ),
    },
    {
        "keywords": ("applied ai", "ai engineer", "machine learning engineer", "ml engineer"),
        "strong_titles": ("ai engineer", "applied ai engineer", "ml engineer", "machine learning engineer"),
        "medium_titles": ("ai", "ml", "machine learning", "applied ai"),
        "skills": (
            "Python", "Machine Learning", "Deep Learning", "MLOps",
            "Inference", "Kubernetes", "CI/CD",
        ),
        "career_terms": (
            "machine learning", "ml", "ai", "model", "models", "inference",
            "deployment", "production", "mlops", "pipeline", "monitoring",
        ),
    },
]


@lru_cache(maxsize=4096)
def normalize_skill_name(skill_name: str) -> str:
    """Return a canonical skill name when the skill is in the taxonomy."""
    cleaned = _clean_term(skill_name)
    return SKILL_ALIASES.get(cleaned, skill_name or "")


@lru_cache(maxsize=4096)
def is_relevant_skill(skill_name: str) -> bool:
    """Use normalized exact matching instead of broad substring matching."""
    return normalize_skill_name(skill_name) in RELEVANT_SKILL_SET


@lru_cache(maxsize=4096)
def normalize_reasoning_skill_name(skill_name: str) -> str:
    """Return the recruiter-facing skill name used only in explanations."""
    cleaned = _clean_term(skill_name)
    if cleaned in REASONING_SKILL_ALIASES:
        return REASONING_SKILL_ALIASES[cleaned]

    for pattern, display_name in REASONING_SKILL_ALIAS_PATTERNS:
        if pattern.search(cleaned):
            return display_name

    canonical = normalize_skill_name(skill_name)
    if canonical == "Large Language Model":
        return "LLMs"
    return canonical


@lru_cache(maxsize=4096)
def reasoning_skill_tier(skill_name: str) -> str:
    """Classify a skill for explanation selection without affecting ranking."""
    display_name = normalize_reasoning_skill_name(skill_name)
    if display_name in DIFFERENTIATOR_REASONING_SKILLS:
        return "differentiator"
    if display_name in CORE_REASONING_SKILLS:
        return "core"
    return ""


def extract_jd_keywords():
    return RELEVANT_SKILLS, PRODUCTION_TERMS, STRONG_TITLES, MEDIUM_TITLES


def _add_skill_aliases_from_text(text: str, relevant: set):
    cleaned_text = f" {_clean_term(text)} "
    for alias, canonical in SKILL_ALIASES.items():
        if f" {alias} " in cleaned_text:
            relevant.add(canonical)


def _clean_terms(values) -> set:
    return {
        cleaned
        for value in values
        for cleaned in [_clean_term(str(value))]
        if cleaned
    }


def parse_jd_context(jd_payload: dict) -> dict:
    """
    Parse a recruiter-supplied JD into a scoring context.
    Returns a dict with:
      - strong_titles: list of lowered title fragments for strong match
      - medium_titles: list of lowered title fragments for medium match
      - relevant_skills: set of canonical skill names to match against
      - exp_min / exp_max: experience band (defaults to 5-9 if unspecified)

    When jd_payload is None or empty, returns None (signals use defaults).
    """
    if not jd_payload:
        return None

    context = {}

    # --- Title keywords from the role field ---
    role = (jd_payload.get("role") or "").lower().strip()
    role_clean = _clean_term(role)
    matched_profiles = [
        profile
        for profile in ROLE_JD_PROFILES
        if any(keyword in role_clean for keyword in profile["keywords"])
    ]

    if role:
        # Build strong title patterns from the role.
        # e.g. "Senior Machine Learning Engineer" -> ["machine learning engineer", "ml engineer"]
        strong = set()
        medium = set()
        # The full role (minus common prefixes) is a strong match
        for prefix in ("senior ", "staff ", "principal ", "lead ", "founding ", "head "):
            if role.startswith(prefix):
                role_core = role[len(prefix):]
                strong.add(role_core)
                break
        else:
            role_core = role
        role_core_clean = _clean_term(role_core)
        strong.add(role_core_clean)
        strong.add(role_clean)

        # Extract useful sub-fragments for medium matching
        role_words = role_core_clean.split()
        if len(role_words) >= 2:
            # Add key role terms as medium matches
            for term in role_words:
                if term not in ("engineer", "scientist", "analyst", "developer",
                                "specialist", "architect", "researcher", "manager",
                                "the", "a", "an", "and", "or", "of", "for"):
                    medium.add(term)

        for profile in matched_profiles:
            strong.update(profile["strong_titles"])
            medium.update(profile["medium_titles"])

        context["strong_titles"] = [t for t in strong if len(t) > 1]
        context["medium_titles"] = [t for t in medium if len(t) > 1]
    else:
        context["strong_titles"] = list(STRONG_TITLES)
        context["medium_titles"] = list(MEDIUM_TITLES)

    # --- Skills from must_have_skills + nice_to_have_skills ---
    jd_skills_raw = []
    for key in ("must_have_skills", "nice_to_have_skills"):
        val = jd_payload.get(key)
        if isinstance(val, list):
            jd_skills_raw.extend(val)

    # Also try to extract skills from a free-text "job_description" field
    jd_text = jd_payload.get("job_description") or jd_payload.get("description") or ""
    if isinstance(jd_text, str) and jd_text:
        jd_text_lower = _clean_term(jd_text)
        for alias, canonical in SKILL_ALIASES.items():
            if alias in jd_text_lower:
                jd_skills_raw.append(canonical)

    for profile in matched_profiles:
        jd_skills_raw.extend(profile["skills"])

    relevant = set()
    if jd_skills_raw:
        for skill_name in jd_skills_raw:
            canonical = normalize_skill_name(str(skill_name))
            if canonical in RELEVANT_SKILL_SET:
                relevant.add(canonical)
            else:
                # Check if any alias matches
                cleaned = _clean_term(str(skill_name))
                matched = SKILL_ALIASES.get(cleaned)
                if matched:
                    relevant.add(matched)
                else:
                    # Add raw skill for substring matching
                    relevant.add(str(skill_name).strip())
            _add_skill_aliases_from_text(str(skill_name), relevant)

    if isinstance(jd_text, str) and jd_text:
        _add_skill_aliases_from_text(jd_text, relevant)

    context["relevant_skills"] = relevant
    context["skill_terms"] = _clean_terms(relevant)
    context["skill_term_set"] = set(context["skill_terms"])
    context["debug_skills"] = sorted(relevant)

    career_terms = set(context["skill_terms"])
    career_terms.update(_clean_terms(context["strong_titles"]))
    career_terms.update(_clean_terms(context["medium_titles"]))
    for profile in matched_profiles:
        career_terms.update(_clean_terms(profile["career_terms"]))
    for skill_name in jd_skills_raw:
        career_terms.update(_clean_terms([skill_name]))
    context["career_terms"] = sorted(career_terms)
    context["career_term_tokens"] = tuple(
        f" {term} "
        for term in context["career_terms"]
    )

    # --- Experience band ---
    exp_str = jd_payload.get("experience") or ""
    exp_min, exp_max = 5, 9  # defaults matching original code
    if isinstance(exp_str, str):
        import re as _re
        numbers = _re.findall(r"(\d+)", exp_str)
        if len(numbers) >= 2:
            exp_min = int(numbers[0])
            exp_max = int(numbers[1])
        elif len(numbers) == 1:
            exp_min = max(int(numbers[0]) - 2, 0)
            exp_max = int(numbers[0]) + 2

    context["exp_min"] = exp_min
    context["exp_max"] = exp_max

    return context

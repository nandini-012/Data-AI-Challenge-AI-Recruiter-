"""Skill and evidence vocabulary used by the ranking pipeline."""

import re


def _clean_term(value: str) -> str:
    """Normalize punctuation/spacing before taxonomy lookup."""
    value = (value or "").lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9+#.]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


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


def normalize_skill_name(skill_name: str) -> str:
    """Return a canonical skill name when the skill is in the taxonomy."""
    cleaned = _clean_term(skill_name)
    return SKILL_ALIASES.get(cleaned, skill_name or "")


def is_relevant_skill(skill_name: str) -> bool:
    """Use normalized exact matching instead of broad substring matching."""
    return normalize_skill_name(skill_name) in RELEVANT_SKILL_SET


def normalize_reasoning_skill_name(skill_name: str) -> str:
    """Return the recruiter-facing skill name used only in explanations."""
    cleaned = _clean_term(skill_name)
    if cleaned in REASONING_SKILL_ALIASES:
        return REASONING_SKILL_ALIASES[cleaned]

    for alias, display_name in REASONING_SKILL_ALIASES.items():
        if re.search(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])", cleaned):
            return display_name

    canonical = normalize_skill_name(skill_name)
    if canonical == "Large Language Model":
        return "LLMs"
    return canonical


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

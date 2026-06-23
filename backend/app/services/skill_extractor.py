# Relevant skills weighted by duration and endorsements
RELEVANT_SKILLS = [
    "python", "pytorch", "tensorflow", "machine learning",
    "deep learning", "nlp", "llm", "transformers",
    "computer vision", "mlops", "sql", "spark",
    "embeddings", "faiss", "vector search",
    "fine-tuning llms", "sentence transformers",
    "elasticsearch", "information retrieval",
    "recommendation systems", "hugging face transformers",
    "lora", "opensearch", "milvus", "langchain"
]

PRODUCTION_TERMS = [
    "deployed", "production", "shipped", "scaled", "users",
    "latency", "throughput", "pipeline", "infrastructure", "launched"
]

STRONG_TITLES = [
    "ai engineer", "ml engineer", "machine learning engineer",
    "research scientist", "applied scientist"
]

MEDIUM_TITLES = [
    "data scientist", "ai", "ml", "machine learning"
]

def extract_jd_keywords():
    return RELEVANT_SKILLS, PRODUCTION_TERMS, STRONG_TITLES, MEDIUM_TITLES
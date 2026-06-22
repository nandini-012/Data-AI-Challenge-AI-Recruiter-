# These are the exact skills the JD asks for
JD_REQUIRED_SKILLS = {
    "embeddings", "vector", "retrieval", "ranking",
    "nlp", "llm", "fine-tuning", "faiss", "pinecone",
    "qdrant", "weaviate", "elasticsearch", "python",
    "rag", "sentence-transformers", "search",
    "recommendation", "milvus", "openai", "bge",
    "lora", "qlora", "peft", "xgboost", "bert",
    "transformers", "pytorch", "huggingface"
}

# Skills that are nice to have but not must-have
JD_BONUS_SKILLS = {
    "aws", "gcp", "azure", "docker", "kubernetes",
    "mlflow", "wandb", "weights & biases", "fastapi",
    "flask", "spark", "kafka", "airflow"
}

def extract_jd_keywords() -> tuple:
    """
    Returns required and bonus skill sets from the JD.
    No need to parse text — we know the JD already.
    """
    return JD_REQUIRED_SKILLS, JD_BONUS_SKILLS 

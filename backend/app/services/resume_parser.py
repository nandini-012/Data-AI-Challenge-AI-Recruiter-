import gzip
import json

def load_candidates(path: str) -> list:
    """
    Loads candidates.jsonl or candidates.jsonl.gz file line by line.
    Each line is one candidate JSON object.
    Returns list of all 100,000 candidates.
    Handles both compressed (.gz) and uncompressed (.jsonl) files.
    """
    candidates = []

    if path.endswith(".gz"):
        opener = gzip.open(path, "rt", encoding="utf-8")
    else:
        opener = open(path, "r", encoding="utf-8")

    with opener as f:
        for line in f:
            line = line.strip()
            if line:
                candidates.append(json.loads(line))

    return candidates 
from __future__ import annotations
import chromadb, hashlib, pathlib, numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

CHROMA_DIR = pathlib.Path(".chroma_viralvisor")
COLL_NAME  = "captions"

embedder = SentenceTransformer('all-MiniLM-L6-v2')

# embedding function for hugging face 
class HFEmbeddingFunction:
    def __call__(self, texts):
        return embedder.encode(texts).tolist()

embedding_function = HFEmbeddingFunction() 

client = chromadb.PersistentClient(path=str(CHROMA_DIR)) #chroma db for storing captions

try:
    # Try to get the collection
    coll = client.get_collection(COLL_NAME, embedding_function=embedding_function)
except chromadb.errors.NotFoundError:
    # Create collection if not found
    coll = client.create_collection(COLL_NAME, embedding_function=embedding_function)

def add_caption(text: str):
    """Add caption text to vector DB (id = md5 hash)."""
    cid = hashlib.md5(text.encode("utf-8")).hexdigest()
    try:
        coll.add(ids=[cid], documents=[text])
    except chromadb.errors.IDAlreadyExistsError:
        pass


# computer similarity betw the input text and stored caption
def similarity(text: str, k: int = 5) -> float:
    """Return similarity 0-1 (higher = more similar)."""
    if coll.count() == 0:
        return 0.0
    res = coll.query(query_texts=[text], n_results=min(k, coll.count()))
    dists = res["distances"][0]
    return round(1 / (1 + np.mean(dists)), 3)
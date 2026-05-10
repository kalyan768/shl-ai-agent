import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

print("Loading model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

print("Model loaded.")

with open("catalog.json", "r", encoding="utf-8") as f:
    catalog = json.load(f)

texts = [item["name"] for item in catalog]

print("Creating embeddings...")

embeddings = model.encode(texts)

print("Embeddings created.")


def recommend_assessments(query, top_k=5):

    query_embedding = model.encode([query])

    similarities = cosine_similarity(query_embedding, embeddings)[0]

    ranked_indices = similarities.argsort()[::-1][:top_k]

    results = []

    for idx in ranked_indices:

        item = catalog[idx]

        results.append(
            {"name": item["name"], "url": item["url"], "test_type": "Unknown"}
        )

    return results

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def get_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')


def build_product_embeddings(df_product, model):
    df = df_product[df_product["name"].astype(str).str.strip() != ""].drop_duplicates(subset=["id"])
    metadata = [{"product_id": str(row["id"]), "product_name": row["name"]} for _, row in df.iterrows()]
    names = [m["product_name"] for m in metadata]
    embeddings = model.encode(names, show_progress_bar=False)
    return np.array(embeddings), metadata


def build_customer_embeddings(df_customers, model):
    df = df_customers[df_customers["full_name"].astype(str).str.strip() != ""].drop_duplicates(subset=["id"])
    metadata = [{"customer_id": str(row["id"]), "customer_name": row["full_name"]} for _, row in df.iterrows()]
    names = [m["customer_name"] for m in metadata]
    embeddings = model.encode(names, show_progress_bar=False)
    return np.array(embeddings), metadata


def similarity_search(query, embeddings, metadata, model, top_k=10):
    if len(metadata) == 0:
        return []
    query_embedding = model.encode([query], show_progress_bar=False)
    scores = cosine_similarity(query_embedding, embeddings)[0]
    top_indices = np.argsort(scores)[::-1][:top_k]
    results = []
    for i in top_indices:
        entry = dict(metadata[i])
        entry["similarity"] = round(float(scores[i]), 3)
        results.append(entry)
    return results

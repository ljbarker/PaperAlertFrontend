import os
import random
import json
from adapters import AutoAdapterModel
from transformers import AutoTokenizer
import torch
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm


# Load the Specter++ model with the Specter2 adapter
def load_model():
    try:
        model = AutoAdapterModel.from_pretrained("allenai/specter_plus_plus")
        model.load_adapter("allenai/specter2", set_active=True)
        tokenizer = AutoTokenizer.from_pretrained("allenai/specter_plus_plus")
        return model, tokenizer
    except OSError as e:
        print(f"Error loading model: {e}")
        raise


# Function to extract [CLS] embeddings
def get_cls_embedding(text, tokenizer, model):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    cls_embedding = outputs.last_hidden_state[:, 0, :]
    return cls_embedding.squeeze(0)


# Function to aggregate [CLS] embeddings for title, summary, and content
def get_aggregated_embedding(entry, tokenizer, model, title_weight=1.0, summary_weight=1.5, content_weight=1.0):
    title_embedding = get_cls_embedding(entry["title"], tokenizer, model) * title_weight
    summary_embedding = get_cls_embedding(entry["summary"], tokenizer, model) * summary_weight
    content_embedding = get_cls_embedding(entry["content"], tokenizer, model) * content_weight
    return title_embedding + summary_embedding + content_embedding


# Function to compute similarity scores
def compute_similarities(query_text, dataset_entries, model, tokenizer):
    query_embedding = get_cls_embedding(query_text, tokenizer, model)
    query_embedding = query_embedding / query_embedding.norm(dim=0)

    scores = []
    for entry in tqdm(dataset_entries, desc="Processing entries", unit="entry"):
        entry_embedding = get_aggregated_embedding(entry, tokenizer, model)
        entry_embedding = entry_embedding / entry_embedding.norm(dim=0)

        score = cosine_similarity(query_embedding.unsqueeze(0).numpy(), entry_embedding.unsqueeze(0).numpy())[0][0]
        scores.append({"entry": entry, "score": score})

    return scores


# Function to load JSONL dataset
def load_jsonl(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


# Main execution
if __name__ == "__main__":
    dataset_path = "/Users/dhern162/Downloads/train.jsonl"
    dataset = load_jsonl(dataset_path)

    random_entry = random.choice(dataset)
    abstract = random_entry["summary"]
    query_text = random_entry["content"]

    model, tokenizer = load_model()

    similarities = compute_similarities(abstract, dataset, model, tokenizer)
    ranked_results = sorted(similarities, key=lambda x: x["score"], reverse=True)

    print("\nQuery Entry:")
    print(f"Title: {random_entry['title']}")
    print(f"Summary: {random_entry['summary']}")

    print("Top Relevant Papers:")
    for i, result in enumerate(ranked_results[:5]):
        entry = result["entry"]
        score = result["score"]
        print(f"Rank {i + 1}:")
        print(f" Title: {entry['title']}")
        print(f" Score: {score:.4f}")
        print(f" Summary: {entry['summary']}\n")

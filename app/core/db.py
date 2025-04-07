import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import uuid
from typing import List
from app.core.settings import groq_client
import hashlib

# Init Chroma client
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("user_conversations")

# Embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def embed(text: str) -> List[float]:
    return embedder.encode([text])[0].tolist()

def get_doc_id(user_id: str, role: str, content: str) -> str:
    # Use hash to uniquely identify the message
    content_hash = hashlib.md5(content.encode()).hexdigest()
    return f"{user_id}_{role}_{content_hash}"


def store_to_vector_db(user_id: str, role: str, content: str, chat_type: str = "tutor"):
    doc_id = get_doc_id(user_id, role, content)
    collection.add(
        documents=[content],
        metadatas=[{"user_id": user_id, "role": role, "chat_type": chat_type}],
        ids=[doc_id],
        embeddings=[embed(content)],
    )

def get_previous_context(user_id: str, query: str, chat_type: str, top_k_similar: int = 20, recent_k: int = 20) -> List[dict]:
    # Step 1: Fetch all documents for this user
    all_user_data = collection.get(where={"user_id": user_id})

    # Step 2: Filter by chat_type manually
    filtered_docs_with_meta = [
        (doc, meta)
        for doc, meta in zip(all_user_data.get("documents", []), all_user_data.get("metadatas", []))
        if meta.get("chat_type") == chat_type
    ]

    # Step 3: If no past chats in this role, return []
    if not filtered_docs_with_meta:
        return []

    # Step 4: Run similarity search (still only filter by user_id)
    similar_results = collection.query(
        query_embeddings=[embed(query)],
        n_results=top_k_similar,
        where={"user_id": user_id}
    )

    # Step 5: Again, filter by chat_type manually
    similar_docs = [
        doc for doc, meta in zip(similar_results.get("documents", [[]])[0], similar_results.get("metadatas", [[]])[0])
        if meta.get("chat_type") == chat_type
    ]

    # Step 6: Get recent `chat_type`-filtered docs (limit by `recent_k`)
    recent_docs = [doc for doc, _ in filtered_docs_with_meta[:recent_k]]

    # Step 7: Merge and deduplicate
    all_docs = list(dict.fromkeys(similar_docs + recent_docs))

    return [{'role': 'system', 'content': f"Past message: {doc}"} for doc in all_docs]




user_conversations = {}
def chat_with_memory(
    prompt: str,
    user_id: str,
    role_key: str,
    system_prompt_func: callable,
    model_name: str = 'llama3-70b-8192'
) -> str:
    key = f"{user_id}_{role_key}"

    # Step 1: Fetch past context ONLY for this specific API/role
    past_messages = get_previous_context(user_id, prompt, role_key)

    # Step 2: Initialize conversation memory if needed
    if key not in user_conversations:
        system_prompt = system_prompt_func()
        user_conversations[key] = [{'role': 'system', 'content': system_prompt}]
        if past_messages:
            user_conversations[key].extend(past_messages)

    # Step 3: Append user message
    user_conversations[key].append({'role': 'user', 'content': prompt})

    try:
        # Step 4: Generate response from LLM
        chat_completion = groq_client.chat.completions.create(
            messages=user_conversations[key],
            model=model_name
        )
        response = chat_completion.choices[0].message

        # Step 5: Store to vector DB (include role_key as chat_type)
        store_to_vector_db(user_id, "user", prompt, chat_type=role_key)
        store_to_vector_db(user_id, "assistant", response.content, chat_type=role_key)

        # Step 6: Append assistant response to memory
        user_conversations[key].append(response)

        return response.content

    except Exception as e:
        print(f"[ERROR in chat_with_memory ({role_key})]: {e}")
        return "Oops! Something went wrong while generating the response."

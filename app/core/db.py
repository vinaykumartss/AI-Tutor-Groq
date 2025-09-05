import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import uuid
from typing import List
from app.core.settings import groq_client
import hashlib
import json
import os
from json import JSONDecodeError
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

def get_previous_context(user_id: str, query: str, chat_type: str, top_k_similar: int = 10, recent_k: int = 10) -> List[dict]:
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
    model_name: str = 'openai/gpt-oss-20b',
    new_chat: bool = False
) -> str:
    key = f"{user_id}_{role_key}"
    filename = f"{key}.json"
    save_path = os.path.join("conversations", filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    if new_chat and os.path.exists(save_path):
        os.remove(save_path)

    # Step 1: Initialize conversation memory if needed
    if key not in user_conversations:
        if role_key in ['interviewer', 'tutor']:
            system_prompt = system_prompt_func()
        else:
            system_prompt = system_prompt_func(prompt)
        user_conversations[key] = [{'role': 'system', 'content': system_prompt}]

    # Step 2: Append current user message
    user_conversations[key].append({'role': 'user', 'content': prompt})

    # Step 3: Slice last 5 interactions (+ system)
    past_messages = user_conversations[key]
    system_prompt = past_messages[0]
    interaction_messages = past_messages[1:]  # skip system prompt
    last_5_interactions = interaction_messages[-10:]  # 5 user-assistant pairs → 10 messages

    messages_for_llm = [system_prompt] + last_5_interactions
    try:
        # start_time = time.time()
        chat_completion = groq_client.chat.completions.create(
            messages=messages_for_llm,
            model=model_name
        )
        # if hasattr(chat_completion, 'usage'):
        #     print("Prompt tokens:", chat_completion.usage.prompt_tokens)
        #     print("Completion tokens:", chat_completion.usage.completion_tokens)
        #     print("Total tokens:", chat_completion.usage.total_tokens)
        #
        # end_time = time.time()
        # response_time = end_time - start_time
        # print(f"Response time: {response_time:.4f} seconds")

        response = chat_completion.choices[0].message

        # Step 4: Store to vector DB
        store_to_vector_db(user_id, "user", prompt, chat_type=role_key)
        store_to_vector_db(user_id, "assistant", response.content, chat_type=role_key)

        # Step 4: Store interaction to disk
        new_entry = [
            {'role': 'user', 'content': prompt},
            {'role': 'assistant', 'content': response.content}
        ]

        if os.path.exists(save_path):
            with open(save_path, 'r') as f:
                existing_data = json.load(f)
        else:
            existing_data = []

        existing_data.extend(new_entry)

        with open(save_path, 'w') as f:
            json.dump(existing_data, f, indent=2)

        # Step 5: Update full memory (still in memory for long-term)
        user_conversations[key].extend(new_entry)

        return response.content

    except Exception as e:
        print(f"[ERROR in chat_with_memory ({role_key})]: {e}")
        return "Oops! Something went wrong while generating the response."

def conversation_report(
    user_id: str,
    role_key: str,
    system_prompt_func: callable,
    model_name: str = 'llama3-8b-8192'
) -> dict:
    try:
        # Step 1: Construct file path
        filename = f"{user_id}_{role_key}.json"
        file_path = os.path.join("conversations", filename)

        # Step 2: Load the conversation JSON
        if not os.path.exists(file_path):
            return {
                "success": False,
                "error": f"No conversation found for user: {user_id} and role: {role_key}"
            }

        with open(file_path, 'r') as f:
            conversation_data = json.load(f)

        # Step 3: Reconstruct user conversation text
        user_convo_lines = [
            f"{msg['role'].capitalize()}: {msg['content']}"
            for msg in conversation_data if msg['role'] in ['user', 'assistant']
        ]
        conversation_history = "\n".join(user_convo_lines)

        # Step 4: Build prompt using your scoring prompt function
        full_prompt = system_prompt_func(conversation_history)

        # Step 5: Send to LLM
        chat_completion = groq_client.chat.completions.create(
            messages=[{'role': 'user', 'content': full_prompt}],
            model=model_name
        )
        response_text = chat_completion.choices[0].message.content
        # Step 2: Create new prompt asking LLM to return clean JSON
        json_correction_prompt = f"""
        STRICT INSTRUCTION: Respond ONLY with valid JSON. Do not include anything else — no comments, no introductions, no backticks. Just return clean JSON:

        {response_text}
        """
        # Step 3: Send the response_text to LLM for JSON correction
        json_completion = groq_client.chat.completions.create(
            messages=[{'role': 'user', 'content': json_correction_prompt}],
            model=model_name
        )
        response = json_completion.choices[0].message.content
        # Step 6: Try to parse JSON
        try:
            parsed_data = json.loads(response)
            # If parsed_data already follows your desired structure, return it directly
            if all(k in parsed_data for k in
                   ["vocabulary_score", "fluency_score", "intonation_score", "grammar_score", "grammar_corrections"]):
                return parsed_data
            else:
                # If it has its own success/data nesting, flatten it
                return parsed_data

        except JSONDecodeError:
            print("[WARNING] Invalid JSON detected. Returning default scores.")
            return {
                    "vocabulary_score": 0,
                    "fluency_score": 0,
                    "intonation_score": 0,
                    "grammar_score": 0,
                    "grammar_corrections": []
            }

    except Exception as e:
        print(f"[ERROR in conversation_report]: {e}")
        return {
            "success": False,
            "error": "An error occurred while generating the conversation report."
        }
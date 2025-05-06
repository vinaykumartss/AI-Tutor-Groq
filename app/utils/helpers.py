from app.core.settings import groq_client

COUNTRY_DB = "user_country.json"

import os
import json


def load_user_country(user_id: str) -> str:
    print(f"Checking if file exists: {os.path.exists(COUNTRY_DB)}")

    # Check if the country database file exists
    if not os.path.exists(COUNTRY_DB):
        print("Database file doesn't exist.")
        return None  # Return None if the file doesn't exist

    try:
        # Attempt to open and load the JSON data
        with open(COUNTRY_DB, "r") as f:
            data = json.load(f)  # Try to load JSON data

        # If the user ID is found, return it; otherwise, return an empty string
        print(f"Loaded data: {data}")
        return data.get(user_id, "")

    except json.JSONDecodeError:
        # Handle case where JSON is malformed
        print("Error: Malformed JSON in the database file.")
        return None  # Return None if JSON is malformed

    except Exception as e:
        # Handle any other unexpected errors
        print(f"Unexpected error: {e}")
        return None  # Return None for other exceptions


def save_user_country(user_id: str, country: str):
    data = {}

    if os.path.exists(COUNTRY_DB):
        try:
            with open(COUNTRY_DB, "r") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
        except json.JSONDecodeError:
            # Log warning or ignore malformed JSON
            data = {}

    data[user_id] = country

    with open(COUNTRY_DB, "w") as f:
        json.dump(data, f, indent=2)
def is_country_name(prompt: str, model_name: str) -> dict:
    country_check_prompt = {
        "messages": [
            {
                "role": "system",
                "content": (
                    """You are an assistant that only replies in JSON format.
Your task is to detect whether a specific country name is explicitly mentioned in the user's input.

If the input includes a valid, explicit country name, respond:
{"country": "yes", "name": "Country Name"}

If no country name is mentioned or the input is vague (e.g., "What is the capital?"), respond:
{"country": "no", "name": null}

Strictly respond only with the JSON object. Do not explain or include anything else."""
                )
            },
            {"role": "user", "content": prompt}
        ],
        "model": model_name
    }

    # Get the model's response
    response = groq_client.chat.completions.create(**country_check_prompt)
    raw = response.choices[0].message.content.strip()
    print("Raw response:", raw)

    try:
        data = json.loads(raw)
        return data
    except json.JSONDecodeError:
        return {"country": "no", "name": None}


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
STATE_DB = "state_db.json"  # Define this at the top of your module

def load_user_state(user_id: str) -> str:
    print(f"Checking if file exists: {os.path.exists(STATE_DB)}")

    if not os.path.exists(STATE_DB):
        print("State database file doesn't exist.")
        return None

    try:
        with open(STATE_DB, "r") as f:
            data = json.load(f)
        print(f"Loaded state data: {data}")
        return data.get(user_id, "")
    except json.JSONDecodeError:
        print("Error: Malformed JSON in the state database file.")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def save_user_state(user_id: str, state: str):
    data = {}

    if os.path.exists(STATE_DB):
        try:
            with open(STATE_DB, "r") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
        except json.JSONDecodeError:
            data = {}

    data[user_id] = state

    with open(STATE_DB, "w") as f:
        json.dump(data, f, indent=2)

def is_country_name(prompt: str, model_name: str) -> dict:
    country_check_prompt = {
        "messages": [
            {
                "role": "system",
                "content": (
                    """You are an assistant that only replies in JSON format.
Your task is to detect whether a valid country name or state/province name is explicitly mentioned in the user's input.

Rules:
- If a valid country is mentioned, set "country": "yes" and provide the name in "country_name".
- If a valid state or province is mentioned, set "state": "yes" and provide the name in "state_name".
- If either is missing, use "no" and set name as null.

- Stricly check whether the input contains a valid country name.

Respond strictly in this JSON format:
{
  "country": "yes" or "no",
  "country_name": "Country Name" or null,
  "state": "yes" or "no",
  "state_name": "State or Province Name" or null
}
Strictly return only the JSON object. Do not explain."""
                )
            },
            {"role": "user", "content": prompt}
        ],
        "model": model_name
    }

    # Call model
    response = groq_client.chat.completions.create(**country_check_prompt)
    raw = response.choices[0].message.content.strip()
    print("Raw response:", raw)

    try:
        data = json.loads(raw)
        return data
    except json.JSONDecodeError:
        return {
            "country": "no",
            "country_name": None,
            "state": "no",
            "state_name": None
        }


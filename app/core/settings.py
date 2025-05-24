from groq import Groq
from dotenv import load_dotenv
import os
from cryptography.fernet import Fernet

# Load environment variables from .env file
load_dotenv()

# Get the encryption key and encrypted API key from .env
fernet_key = os.getenv("FERNET_KEY")
encrypted_api_key = os.getenv("ENCRYPTED_API_KEY")

# Decrypt the API key
fernet = Fernet(fernet_key.encode())
api_key = fernet.decrypt(encrypted_api_key.encode()).decode()

# Use decrypted API key with Groq client
groq_client = Groq(api_key=api_key)

from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('API_KEY')

groq_client = Groq(api_key=API_KEY)
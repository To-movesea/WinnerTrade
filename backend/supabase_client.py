import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load env vars from .env file
load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

def get_supabase_client() -> Client:
    if not url or not key:
        raise ValueError("Supabase URL and Key must be set in environment variables")
    return create_client(url, key)


import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase: Client = create_client(url, key)

print("Checking portfolio stocks...")
try:
    res = supabase.table('portfolio_stocks').select('*').execute()
    print(f"Success! Found {len(res.data)} stocks.")
    for stock in res.data:
        print(f"- {stock['stock_name']} ({stock['stock_code']})")
except Exception as e:
    print("Error:", e)

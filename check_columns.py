
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

print("Checking portfolio_stocks columns...")
try:
    # Try to select the new columns
    res = supabase.table('portfolio_stocks').select('cost,motivation,risk_sell_time').limit(1).execute()
    print("Columns exist!")
except Exception as e:
    print("Error selecting columns (likely missing):", e)

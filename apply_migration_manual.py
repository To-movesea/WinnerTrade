
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load env from backend/.env
load_dotenv(os.path.join(os.path.dirname(__file__), 'backend', '.env'))

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Error: Supabase credentials not found.")
    exit(1)

supabase: Client = create_client(url, key)

# Read SQL file
migration_file = os.path.join(os.path.dirname(__file__), 'supabase', 'migrations', '20250122_add_portfolio.sql')
with open(migration_file, 'r', encoding='utf-8') as f:
    sql = f.read()

print(f"Read SQL from {migration_file}")

# Try to use the REST API to execute SQL via a function if available, 
# or just check if we can query the table to confirm it's missing.

try:
    print("Checking if portfolio_stocks table exists...")
    res = supabase.table('portfolio_stocks').select('count', count='exact').execute()
    print("Table exists! Count:", res.count)
except Exception as e:
    print("Table check failed (expected if table missing):", e)
    
    # Since we cannot execute DDL via the python client directly without a helper function on the server,
    # and we don't have direct postgres access here easily (unless we install psycopg2 and have the connection string),
    # we will rely on the Tool 'supabase_apply_migration'.
    
    print("\nIMPORTANT: Please use the 'supabase_apply_migration' tool from the assistant capabilities.")

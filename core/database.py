import os
from dotenv import load_dotenv

load_dotenv("moneymagic.env")
# Supabase Python client (supabase-py)
try:
	from supabase import create_client  # type: ignore
except Exception:
	create_client = None

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = None

def get_supabase_client():
    if create_client and SUPABASE_URL and SUPABASE_KEY:
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception:
            supabase = None
    return supabase
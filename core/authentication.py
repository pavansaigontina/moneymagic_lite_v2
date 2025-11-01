from typing import Any, Dict, Optional
from core.database import get_supabase_client

supabase = get_supabase_client()

def _ensure_client():
	if not supabase:
		raise RuntimeError("Supabase client is not configured. Set SUPABASE_URL and SUPABASE_KEY in env.")


def sign_up(email: str, password: str) -> Dict[str, Any]:
	"""Create a new user in Supabase Auth. Returns the auth response dict."""
	_ensure_client()
	res = supabase.auth.sign_up({"email": email, "password": password})
	return res


def sign_in(email: str, password: str) -> Dict[str, Any]:
	"""Sign in an existing user. Returns session/user data."""
	_ensure_client()
	# supabase-py v1 uses sign_in_with_password
	try:
		res = supabase.auth.sign_in_with_password({"email": email, "password": password})
	except Exception:
		# Fallback to older API
		res = supabase.auth.sign_in({"email": email, "password": password})
	return res


def sign_out(access_token: str) -> None:
	_ensure_client()
	try:
		supabase.auth.sign_out()
	except Exception:
		pass
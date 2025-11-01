from core.database import get_supabase_client

def get_all_balances(user_id):
    """
    Get all balances for a user
    """
    supabase = get_supabase_client()
    response = supabase.table('balances')\
        .select('id, month, account_id, opening')\
        .eq('user_id', user_id)\
        .order('month')\
        .execute()
    return response.data if response.data else []

def get_opening(month, account_id, user_id):
    """
    Get opening balance for a specific month (numeric) and account.
    Automatically converts month names like 'November' → 11.
    """
    supabase = get_supabase_client()

    # Convert month name or date to integer (1–12)
    months = [
        'January','February','March','April','May','June',
        'July','August','September','October','November','December'
    ]

    if isinstance(month, str):
        # Try to convert month name to number
        if month.capitalize() in months:
            month_value = months.index(month.capitalize()) + 1
        else:
            # If already numeric string like "11"
            try:
                month_value = int(month)
            except ValueError:
                month_value = None
    elif hasattr(month, "month"):
        # If passed a datetime/date
        month_value = month.month
    else:
        month_value = int(month)

    if month_value is None:
        print(f"⚠️ Invalid month value: {month}")
        return 0.0

    response = (
        supabase.table("balances")
        .select("opening")
        .eq("month", month_value)
        .eq("account_id", account_id)
        .eq("user_id", user_id)
        .order("id", desc=True)
        .limit(1)
        .execute()
    )

    if response.data and len(response.data) > 0:
        try:
            return float(response.data[0].get("opening", 0.0))
        except (TypeError, ValueError):
            return 0.0
    else:
        return 0.0



def set_opening(month, account_id, opening, user_id):
    """
    Set opening balance for a specific month and account
    """
    supabase = get_supabase_client()
    
    # Convert month to number if it's a name
    from core.utils import MONTHS
    if isinstance(month, str) and month in MONTHS:
        month = str(MONTHS.index(month) + 1)
    
    # First check if a record exists
    response = supabase.table('balances')\
        .select('id')\
        .eq('month', month)\
        .eq('account_id', account_id)\
        .eq('user_id', user_id)\
        .execute()
    
    data = {
        'month': month,
        'account_id': account_id,
        'user_id': user_id,
        'opening': float(opening)
    }
    
    if response.data:
        # Update existing record
        response = supabase.table('balances')\
            .update(data)\
            .eq('month', month)\
            .eq('account_id', account_id)\
            .eq('user_id', user_id)\
            .execute()
    else:
        # Insert new record
        response = supabase.table('balances')\
            .insert(data)\
            .execute()
    
    return response.data[0] if response.data else None

from core.database import get_supabase_client

def get_accounts(user_id):
    """
    Fetch all accounts for a specific user.
    """
    supabase = get_supabase_client()
    response = supabase.table('accounts')\
        .select('id, name, type, notes, user_id')\
        .eq('user_id', user_id)\
        .order('name')\
        .execute()
    return response.data if response.data else []


def add_account(name, atype, notes='', user_id=None):
    """
    Add a new account for this user.
    """
    supabase = get_supabase_client()
    data = {
        'name': name,
        'type': atype,
        'notes': notes,
        'user_id': user_id
    }
    response = supabase.table('accounts').insert(data).execute()
    return response.data[0] if response.data else None


def update_account(account_id, name=None, atype=None, notes=None, user_id=None):
    """
    Update an account if owned by this user.
    """
    supabase = get_supabase_client()
    data = {}
    
    if name is not None:
        data['name'] = name
    if atype is not None:
        data['type'] = atype
    if notes is not None:
        data['notes'] = notes
        
    if not data:
        return  # nothing to update
    
    response = supabase.table('accounts')\
        .update(data)\
        .eq('id', account_id)\
        .eq('user_id', user_id)\
        .execute()
     
    return response.data[0] if response.data else None


def delete_account(account_id, user_id=None):
    """
    Delete account if owned by user.
    Prevent deletion if linked transactions exist.
    """
    supabase = get_supabase_client()
    
    # Check for existing transactions
    trans_response = supabase.table('transactions')\
        .select('count')\
        .eq('account_id', account_id)\
        .execute()
    if trans_response.data and len(trans_response.data) > 0:
        raise Exception("Cannot delete account with existing transactions.")
    
    response = supabase.table('accounts')\
        .delete()\
        .eq('id', account_id)\
        .eq('user_id', user_id)\
        .execute()
    return response.data[0] if response.data else None

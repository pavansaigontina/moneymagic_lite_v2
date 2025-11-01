import datetime
import pandas as pd
from core.database import get_supabase_client

def add_transaction(tx_date, account_id, category, description, tx_type, amount, user_id):
    supabase = get_supabase_client()
    
    data = {
        'date': tx_date.isoformat() if hasattr(tx_date, 'isoformat') else str(tx_date),
        'account_id': account_id,
        'category': category,
        'description': description,
        'type': tx_type,
        'amount': float(amount),
        'user_id': user_id
    }
    
    response = supabase.table('transactions')\
        .insert(data)\
        .execute()
        
    return response.data[0]['tx_uuid'] if response.data else None

def update_transaction_by_uuid(tx_uuid, updates: dict):
    supabase = get_supabase_client()
    
    # Convert any date objects to ISO format
    for key, value in updates.items():
        if hasattr(value, 'isoformat'):
            updates[key] = value.isoformat()
    
    response = supabase.table('transactions')\
        .update(updates)\
        .eq('tx_uuid', tx_uuid)\
        .execute()
        
    return response.data[0] if response.data else None

def delete_transaction_by_uuid(tx_uuid):
    supabase = get_supabase_client()
    
    response = supabase.table('transactions')\
        .delete()\
        .eq('tx_uuid', tx_uuid)\
        .execute()
        
    return response.data[0] if response.data else None

def fetch_transactions(
    month_filter=None, start_date=None, end_date=None,
    account_ids=None, types=None, user_id=None
):
    supabase = get_supabase_client()
    
    # Build query
    query = supabase.table('transactions')\
        .select(
            'tx_uuid, date, account_id, category, description, type, amount, user_id, accounts!inner(name)'
        )

    # Always filter by user_id if provided
    if user_id is not None:
        query = query.eq('user_id', user_id)

    # Handle month filter
    if month_filter:
        months = [
            'January','February','March','April','May','June',
            'July','August','September','October','November','December'
        ]
        month_index = months.index(month_filter) + 1
        year = datetime.datetime.today().year 
        start_of_month = datetime.date(year, month_index, 1)
        # first day of next month, then subtract 1 day
        end_of_month = (start_of_month.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)

        query = query.gte('date', start_of_month.isoformat())
        query = query.lte('date', end_of_month.isoformat())
        

    # Apply optional filters
    if start_date:
        query = query.gte('date', start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date))
    if end_date:
        query = query.lte('date', end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date))

    if account_ids:
        query = query.in_('account_id', account_ids)
    if types and len(types) > 0:
        query = query.in_('type', types)

    # Sort results
    query = query.order('date', desc=True)
    query = query.range(0, 9999)

    # Execute
    response = query.execute()
    
    if not response.data:
        return pd.DataFrame(columns=["Transaction_ID", "Date", "Account", "Category", "Description", "Type", "Amount"])
    
    # Convert to DataFrame
    df_data = []
    for row in response.data:
        account_name = row['accounts']['name'] if row.get('accounts') else None
        df_data.append({
            'Transaction_ID': row['tx_uuid'],
            'Date': pd.to_datetime(row['date']).date(),
            'Account': account_name,
            'Category': row['category'],
            'Description': row['description'],
            'Type': row['type'],
            'Amount': float(row['amount'])
        })
    
    return pd.DataFrame(df_data)
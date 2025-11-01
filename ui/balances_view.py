import streamlit as st
import pandas as pd
from datetime import datetime
from core.accounts import get_accounts
from core.balances import get_opening, set_opening, get_all_balances
from core.utils import MONTHS

def show_balances_view(user):
    st.header("🔧 Balances")
    try:
        accounts = get_accounts(user["id"])
        if not accounts:
            st.info("Add accounts first.")
            return

        # Create a mapping of account IDs to names
        account_names = {a['id']: a['name'] for a in accounts}

        with st.expander("Show Balance Form"):
            with st.form("balance_form"):
                sel_month = st.selectbox("Select month", MONTHS, index=datetime.now().month-1)
                sel_account = st.selectbox("Select account", [a['name'] for a in accounts])
                aid = next((a['id'] for a in accounts if a['name']==sel_account), None)
                
                try:
                    current = get_opening(sel_month, aid, user["id"])
                except Exception as e:
                    st.error(f"Error loading balance: {str(e)}")
                    current = 0.0
                
                new_opening = st.number_input(
                    f"Opening for {sel_account} in {sel_month}", 
                    value=current, 
                    min_value=0.0, 
                    step=100.0, 
                    format="%.2f"
                )
                
                if st.form_submit_button("Save opening"):
                    try:
                        result = set_opening(sel_month, aid, new_opening, user["id"])
                        if result:
                            st.success("Saved opening balance")
                            st.rerun()
                        else:
                            st.error("Failed to save balance. Please try again.")
                    except Exception as e:
                        st.error(f"Error saving balance: {str(e)}")

        # Display balances table
        st.subheader("Opening Balances")
        try:
            balances = get_all_balances(user["id"])
            if balances:
                # Convert balances to DataFrame
                df = pd.DataFrame(balances)
                # Replace account with account name
                df['Account'] = df['account_id'].map(account_names)
                
                # Convert month name to number if it's a string name
                def month_to_number(x):
                    if isinstance(x, str) and x in MONTHS:
                        return str(MONTHS.index(x) + 1)
                    return x
                df['month'] = df['month'].map(month_to_number)
                df['Month'] = df['month'].map(lambda x: MONTHS[int(x)-1])
                df['Opening Balance'] = df['opening'].map('${:,.2f}'.format)
                
                # Reorder and display columns
                df = df[['Month', 'Account', 'Opening Balance']]
                st.dataframe(
                    df,
                    column_config={
                        "Month": st.column_config.TextColumn("Month"),
                        "Account": st.column_config.TextColumn("Account"),
                        "Opening Balance": st.column_config.TextColumn("Opening Balance"),
                    },
                    hide_index=True
                )
            else:
                st.info("No opening balances set yet.")
        except Exception as e:
            st.error(f"Error loading balances table: {str(e)}")
            
    except Exception as e:
        st.error(f"Error loading accounts: {str(e)}")
        return

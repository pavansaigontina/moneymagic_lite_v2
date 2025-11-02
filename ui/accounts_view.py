import streamlit as st
from core.accounts import get_accounts, add_account, update_account, delete_account

def show_accounts_view(user):
    st.header("🏦 Accounts")
    try:
        accounts = get_accounts(user["id"])
    except Exception as e:
        st.error(f"Error loading accounts: {str(e)}")
        accounts = []

    with st.expander("Add account"):
        with st.form("add_account_form"):
            name = st.text_input("Account name")
            atype = st.selectbox("Type", ["Debit","Credit"])
            notes = st.text_area("Notes (optional)")
            if st.form_submit_button("Add account", type="primary"):
                if not name:
                    st.error("Name required")
                else:
                    try:
                        result = add_account(name.strip(), atype, notes.strip(), user["id"])
                        if result:
                            st.success("Account added")
                            st.rerun()
                        else:
                            st.error("Failed to add account. Please try again.")
                    except Exception as e:
                        st.error(f"Error adding account: {str(e)}")

    st.markdown("**Existing accounts**")
    if accounts:
        for a in accounts:
            # Ensure we have all required fields
            if not all(key in a for key in ['id', 'name', 'type', 'notes']):
                st.error(f"Invalid account data: {a}")
                continue

            with st.expander(f"{a['name']} ({a['type']})"):
                st.write(a.get('notes', ''))
                c1, c2, c3 = st.columns([2,1,1])
                with c1:
                    new_name = st.text_input(f"name_{a['id']}", value=a['name'])
                with c2:
                    new_type = st.selectbox(f"type_{a['id']}", ["Debit","Credit"], 
                                          index=0 if a['type']=="Debit" else 1)
                with c3:
                    if st.button("Save", key=f"save_acc_{a['id']}", type="primary"):
                        try:
                            result = update_account(a['id'], 
                                                 name=new_name.strip(), 
                                                 atype=new_type, 
                                                 user_id=user["id"])
                            if result:
                                st.success("Saved")
                                st.rerun()
                            else:
                                st.error("Failed to update account. Please try again.")
                        except Exception as e:
                            st.error(f"Error updating account: {str(e)}")

                if st.button("Delete account", key=f"del_acc_{a['id']}"):
                    try:
                        result = delete_account(a['id'], 
                                             user_id=user["id"])
                        if result is not None:
                            st.success("Deleted")
                            st.rerun()
                        else:
                            st.error("Failed to delete account. Please try again.")
                    except Exception as e:
                        st.error(f"Error deleting account: {str(e)}")
    else:
        st.info("No accounts. Add one above.")

import streamlit as st
from ui.auth import login_page, signup_page, signout_page
from ui.accounts_view import show_accounts_view
from ui.balances_view import show_balances_view
from ui.transactions_view import show_transactions_view

st.set_page_config(
    page_title="Money Magic Lite",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get help": "mailto:pavangontina@zohomail.in", 
        "Report a Bug": "mailto:pavangontina@zohomail.in",
        "About": """
        ### Money Magic Lite 💸  
        A lightweight personal finance tracker.  
        Contact: pavangontina@zohomail.in
        """
    }
)

# Session state to track login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def main_page():
    st.title("MoneyMagic Lite")
    st.caption("Personal Finance Management App - Version 2.0")
    user = st.session_state.user
    if user is not None:
        with st.sidebar:
            st.write(f"Welcome {st.session_state.user['email']}!")
            show_accounts_view(user)
            show_balances_view(user)
            if st.button("Logout", type='primary'):
                signout_page()
                st.rerun()
            st.info("Developed with ❤️ by :green[Pavan Gontina]")
        show_transactions_view(user)


# Toggle between login and signup pages
if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

if not st.session_state.logged_in:
    if st.session_state.show_signup:
        signup_page()
        if st.button("Back to Login"):
            st.session_state.show_signup = False
            st.rerun()
    else:
        login_page()
        if st.button("Create new account"):
            st.session_state.show_signup = True
            st.rerun()
else:
    main_page()

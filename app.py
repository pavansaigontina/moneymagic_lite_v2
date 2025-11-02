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
st.markdown("""
<style>

/* === Base Typography === */
html, body, [class*="css"] {
    font-family: "Segoe UI", sans-serif !important;
    color: #1f2937 !important;  /* Charcoal text */
    background-color: #fefefe !important;
}

/* === Headings === */
h1, h2, h3, h4, h5, h6 {
    color: #1e3a8a !important;
    font-weight: 600 !important;
}

/* === Links === */
a, a:visited, a:hover, a:active {
    color: #1e40af !important;
    text-decoration: none !important;
}
a:hover {
    text-decoration: underline !important;
}

# /* === Buttons === */
# /* === Primary Buttons (normal + form) === */
# button[kind="primary"],
# div[data-testid="stBaseButton-primary"] button,
# div.stButton > button,
# form button {
#     background-color: #1e3a8a !important;
#     color: #ffffff !important;
#     border: 1px solid #1e3a8a !important;
#     border-radius: 6px !important;
#     font-weight: 500 !important;
#     text-shadow: none !important;
# }

# /* Hover / Focus / Active states */
# button[kind="primary"]:hover,
# div[data-testid="stBaseButton-primary"] button:hover,
# div.stButton > button:hover,
# form button:hover {
#     background-color: #1e40af !important;
#     border-color: #1e40af !important;
#     color: #ffffff !important;
# }

# /* === Secondary Buttons (normal + form) === */
# button[kind="secondary"],
# div[data-testid="stBaseButton-secondary"] button {
#     background-color: #f8fafc !important;
#     color: #1e3a8a !important;
#     border: 1px solid #d1d5db !important;
#     border-radius: 6px !important;
#     font-weight: 500 !important;
# }
# button[kind="secondary"]:hover,
# div[data-testid="stBaseButton-secondary"] button:hover {
#     background-color: #e2e8f0 !important;
#     border-color: #cbd5e1 !important;
# }

# /* === Input Fields === */
input, select, textarea {
    border: 1px solid #d1d5db !important;
    border-radius: 6px !important;
    background-color: #ffffff !important;
    color: #1f2937 !important;
}
input:focus, select:focus, textarea:focus {
    border-color: #1e40af !important;
    box-shadow: 0 0 4px rgba(30, 64, 175, 0.3) !important;
    outline: none !important;
}

/* === Metrics Cards === */
div[data-testid="stMetricValue"] {
    border: 1px solid #d1d5db !important;
    border-radius: 8px !important;
    padding: 8px 10px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    text-align:center;
}

# /* === Plotly Chart Container === */
# div[data-testid="stPlotlyChart"] {
#     border: 1px solid #e5e7eb !important;
#     border-radius: 8px !important;
#     padding: 6px !important;
#     background-color: #ffffff !important;
# }

# /* === Sidebar === */
# section[data-testid="stSidebar"] {
#     background-color: #f8fafc !important;
#     border-right: 1px solid #d1d5db !important;
# }
# section[data-testid="stSidebar"] * {
#     color: #1f2937 !important;
# }

# /* === Remove vertical caret line from select boxes === */
# div[data-baseweb="select"] div:before,
# div[data-baseweb="select"] div:after {
#     content: none !important;
# }

# /* Keep your select box styling intact */
# div[data-baseweb="select"] > div {
#     border: 1px solid #d1d5db !important;
#     border-radius: 6px !important;
#     background-color: #ffffff !important;
#     color: #1f2937 !important;
#     box-shadow: none !important;
# }

# /* Slightly adjust text alignment to center vertically */
# div[data-baseweb="select"] span {
#     margin-left: 0 !important;
# }

# /* Make sure arrow icon is visible and themed */
# div[data-baseweb="select"] svg {
#     stroke: #1e3a8a !important;
# }


</style>
""", unsafe_allow_html=True)


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
            if st.button("Logout"):
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

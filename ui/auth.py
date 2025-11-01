import streamlit as st
from core.authentication import sign_in, sign_up, sign_out

if "user" not in st.session_state:
    st.session_state.user = None

def login_page():
    st.header("MoneyMagic Lite")
    st.subheader("🔐 Login")
    with st.form("login_form"):
        login_email = st.text_input("Email", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        login_submitted = st.form_submit_button("Sign in", type='primary')
        if login_submitted:
            try:
                res = sign_in(login_email, login_password)
                # print(res)
                user = None
                if isinstance(res, dict):
                    user = res.get("user") or res.get("data")
                else:
                    user = getattr(res, "user", None)
                if user:
                    uid = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
                    email_addr = user.get("email") if isinstance(user, dict) else getattr(user, "email", login_email)
                    st.session_state.user = {"id": uid, "email": email_addr}
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Sign-in failed. Check SUPABASE settings and credentials.")
            except Exception as e:
                st.error(f"Sign-in error: Please check your credentials and try again.")


def signup_page():
    st.subheader("🔐 Login")
    with st.form("signup_form"):
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        signup_submitted = st.form_submit_button("Create account")
        if signup_submitted:
            try:
                res = sign_up(signup_email, signup_password)
                user = None
                if isinstance(res, dict):
                    user = res.get("user") or res.get("data")
                else:
                    user = getattr(res, "user", None)
                if user:
                    uid = user.get("id") if isinstance(user, dict) else getattr(user, "id", None)
                    st.session_state.user = {"id": uid, "email": signup_email}
                    st.success("Account created. You may need to confirm via email depending on Supabase settings.")
                    st.rerun()
                else:
                    st.info("Registration initiated. Check your email to confirm if required.")
            except Exception as e:
                st.error(f"Sign-up error: {e}")

def signout_page():
    try:
        sign_out(st.session_state.user.get("access_token", ""))
        st.session_state.logged_in = False
        st.session_state.user = None
        st.success("Logged out successfully.")
        st.rerun()
    except Exception as e:
        st.error(f"Sign-out error: {e}")
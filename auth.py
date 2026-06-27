import streamlit as st

# ------------------------------------
# Demo Users
# ------------------------------------

USERS = {
    "doctor": {
        "password": "doctor123",
        "role": "Doctor"
    },
    "coder": {
        "password": "coder123",
        "role": "Medical Coder"
    },
    "admin": {
        "password": "admin123",
        "role": "Administrator"
    }
}

# ------------------------------------
# Login
# ------------------------------------

def login():

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "user_role" not in st.session_state:
        st.session_state.user_role = ""

    if st.session_state.logged_in:
        show_sidebar()
        return

    st.sidebar.title("🔐 Login")

    username = st.sidebar.selectbox(
        "Username",
        USERS.keys()
    )

    password = st.sidebar.text_input(
        "Password",
        type="password"
    )

    if st.sidebar.button("Login"):

        if USERS[username]["password"] == password:

            st.session_state.logged_in = True
            st.session_state.user_role = USERS[username]["role"]

            st.rerun()

        else:

            st.sidebar.error("Invalid Password")

    st.stop()

# ------------------------------------
# Sidebar
# ------------------------------------

def show_sidebar():

    st.sidebar.success(
        f"Logged in as {st.session_state.user_role}"
    )

    st.sidebar.divider()

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.user_role = ""

        st.rerun()

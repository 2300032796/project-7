import streamlit as st

# -----------------------------
# Demo Users
# -----------------------------

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

# -----------------------------
# Login Function
# -----------------------------

def login():

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "role" not in st.session_state:
        st.session_state.role = None

    if st.session_state.logged_in:
        return

    st.sidebar.title("🔐 Login")

    username = st.sidebar.selectbox(
        "Username",
        list(USERS.keys())
    )

    password = st.sidebar.text_input(
        "Password",
        type="password"
    )

    if st.sidebar.button("Login"):

        if USERS[username]["password"] == password:

            st.session_state.logged_in = True
            st.session_state.role = USERS[username]["role"]

            st.sidebar.success("Login Successful")

            st.rerun()

        else:

            st.sidebar.error("Invalid Username or Password")

    st.stop()

# -----------------------------
# Logout Button
# -----------------------------

def logout():

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.role = None

        st.rerun()

# -----------------------------
# Display Current User
# -----------------------------

def show_user():

    if st.session_state.logged_in:

        st.sidebar.success(
            f"Logged in as: {st.session_state.role}"
        )

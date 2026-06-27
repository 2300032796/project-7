import re
import streamlit as st
from datetime import datetime

# =====================================
# Prompt Injection Detection
# =====================================

PROMPT_ATTACKS = [
    "ignore previous instructions",
    "ignore all instructions",
    "system prompt",
    "developer message",
    "act as admin",
    "reveal password",
    "delete database",
    "jailbreak",
    "override",
    "bypass",
    "forget previous",
    "disable safety"
]

def check_prompt_injection(text: str):

    text = text.lower()

    for attack in PROMPT_ATTACKS:

        if attack in text:

            return True

    return False


# =====================================
# Sensitive Data Detection
# =====================================

def detect_sensitive_data(text):

    patterns = {

        "Phone Number":
        r"\b\d{10}\b",

        "Email":
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",

        "Aadhaar":
        r"\b\d{4}\s\d{4}\s\d{4}\b",

        "PAN":
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"

    }

    found = []

    for key, pattern in patterns.items():

        if re.search(pattern, text):

            found.append(key)

    return found


# =====================================
# Medical Safety Check
# =====================================

def medical_guard(question):

    dangerous = [

        "prescribe medicine",

        "change dosage",

        "replace doctor",

        "perform surgery"

    ]

    q = question.lower()

    for word in dangerous:

        if word in q:

            return False

    return True


# =====================================
# Hallucination Check
# =====================================

def hallucination_guard(answer, evidence):

    if len(evidence) == 0:

        return False

    score = 0

    for doc in evidence:

        if len(doc) > 20:

            score += 1

    return score > 0


# =====================================
# Audit Logging
# =====================================

def audit_log(user, question):

    if "audit_logs" not in st.session_state:

        st.session_state.audit_logs = []

    st.session_state.audit_logs.append({

        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "User": user,

        "Question": question

    })


# =====================================
# Display Audit Logs
# =====================================

def show_audit_logs():

    if "audit_logs" not in st.session_state:

        return

    st.subheader("Audit Logs")

    st.dataframe(st.session_state.audit_logs)


# =====================================
# Risk Score
# =====================================

def calculate_risk(question):

    score = 0

    if check_prompt_injection(question):

        score += 60

    if detect_sensitive_data(question):

        score += 20

    if not medical_guard(question):

        score += 20

    if score < 30:

        return score, "Low"

    elif score < 60:

        return score, "Medium"

    else:

        return score, "High"

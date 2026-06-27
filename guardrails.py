import re

PROMPT_ATTACKS = [

    "ignore previous instructions",

    "system prompt",

    "act as admin",

    "jailbreak",

    "developer message",

    "bypass"

]

def detect_prompt_injection(question):

    question = question.lower()

    for attack in PROMPT_ATTACKS:

        if attack in question:

            return True

    return False

def calculate_risk(question):

    score = 0

    if detect_prompt_injection(question):

        score += 60

    if len(question) > 500:

        score += 10

    if re.search(r"\b\d{12}\b", question):

        score += 20

    if score < 30:

        level = "Low"

    elif score < 60:

        level = "Medium"

    else:

        level = "High"

    return score, level

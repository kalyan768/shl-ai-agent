from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from groq import Groq
from dotenv import load_dotenv
import os

from recommender import recommend_assessments
from prompts import SYSTEM_PROMPT

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()

# ---------------- MODELS ---------------- #


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]


# ---------------- HEALTH ---------------- #


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------- CHAT ---------------- #


@app.post("/chat")
def chat(request: ChatRequest):

    messages = request.messages

    latest_user_message = ""

    for msg in reversed(messages):
        if msg.role == "user":
            latest_user_message = msg.content
            break

    user_text = latest_user_message.lower()

    # ---------------- OFF TOPIC ---------------- #

    off_topic_keywords = [
        "salary",
        "legal",
        "law",
        "politics",
        "cricket",
        "movie",
        "weather",
    ]

    if any(word in user_text for word in off_topic_keywords):

        return {
            "reply": "I can only help with SHL assessment recommendations and comparisons.",
            "recommendations": [],
            "end_of_conversation": False,
        }

    # ---------------- COMPARISON ---------------- #

    if "difference" in user_text or "compare" in user_text:

        prompt = f"""
        {SYSTEM_PROMPT}

        Compare these SHL assessments:
        {latest_user_message}

        Give concise comparison using SHL context only.
        """

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        reply_text = completion.choices[0].message.content

        return {
            "reply": reply_text,
            "recommendations": [],
            "end_of_conversation": False,
        }

    # ---------------- CLARIFICATION ---------------- #

    if len(latest_user_message.split()) < 5:

        return {
            "reply": "Could you share the role, experience level, and important skills required?",
            "recommendations": [],
            "end_of_conversation": False,
        }

    # ---------------- RECOMMENDATIONS ---------------- #

    recommendations = recommend_assessments(latest_user_message, top_k=5)

    prompt = f"""
    {SYSTEM_PROMPT}

    User Query:
    {latest_user_message}

    Recommended Assessments:
    {recommendations}

    Explain briefly why these assessments fit.
    """

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    reply_text = completion.choices[0].message.content

    return {
        "reply": reply_text,
        "recommendations": recommendations,
        "end_of_conversation": False,
    }

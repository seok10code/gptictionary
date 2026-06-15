import os
import json
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_word_info(vocabulary: str) -> dict:
    prompt = f"""
        You are an expert English teacher for Korean learners.

        First determine whether the input is a valid English word or phrase.

        Return ONLY valid JSON.
        Do not use markdown.
        Do not add explanations outside JSON.

        If the input is NOT a valid English word or phrase, return:
        {{
        "valid": false
        }}

        If the input IS valid, return:
        {{
        "valid": true,
        "vocabulary": "{vocabulary}",
        "definition": "Natural Korean meaning",
        "sentence": "Natural English example sentence using the word or phrase",
        "synonyms": "synonym1, synonym2, synonym3",
        "usage_note": "Korean nuance explanation + real-life usage + two short English conversation examples"
        }}

        Requirements:
        - definition must be Korean.
        - sentence must be natural everyday English.
        - synonyms should be comma-separated.
        - usage_note must be written mostly in Korean.
        - usage_note must explain how native speakers use it in real conversation.
        - usage_note must include two short realistic English conversation examples.
        - Each conversation example must have A and B lines.
        - Do not make usage_note too long.
        - Avoid dictionary-style explanation only.

        usage_note format:
        "이 표현은 ... 뉘앙스로 쓰입니다. 실제 대화에서는 ... 상황에서 자주 씁니다.

        실제 대화 1:
        A: ...
        B: ...

        실제 대화 2:
        A: ...
        B: ..."

        Input: {vocabulary}
        """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an English teacher. "
                    "Return valid JSON only."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    content = response.choices[0].message.content.strip()

    try:
        return json.loads(content)

    except Exception:
        return {
            "valid": False
        }


def ask_openai(question: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "너는 영어 표현을 한국어로 쉽고 자연스럽게 설명해주는 영어 선생님이야."
            },
            {
                "role": "user",
                "content": question
            }
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content


def extract_word_candidate(question: str, answer: str) -> dict | None:
    prompt = f"""
        You are an expert English teacher for Korean learners.

        From the user's question and the answer, extract ONE useful English word or phrase worth saving to a vocabulary notebook.

        Return ONLY valid JSON.
        Do not use markdown.
        Do not add explanations outside JSON.

        If there is no useful English word or phrase to save, return:
        {{
        "has_candidate": false
        }}

        If there is a useful word or phrase, return:
        {{
        "has_candidate": true,
        "vocabulary": "English word or phrase",
        "definition": "Natural Korean meaning",
        "sentence": "Natural English example sentence using the word or phrase",
        "synonyms": "synonym1, synonym2, synonym3",
        "usage_note": "Korean nuance explanation + real-life usage + two short English conversation examples"
        }}

        Requirements:
        - Pick only ONE best expression.
        - Prefer the expression the user asked about.
        - Do not extract random common words.
        - vocabulary must be English only.
        - definition must be Korean.
        - sentence must be natural everyday English.
        - synonyms should be comma-separated.
        - usage_note must be written mostly in Korean.
        - usage_note must explain how native speakers use it in real conversation.
        - usage_note must include two short realistic English conversation examples.
        - Each conversation example must have A and B lines.
        - Do not make usage_note too long.

        usage_note format:
        "이 표현은 ... 뉘앙스로 쓰입니다. 실제 대화에서는 ... 상황에서 자주 씁니다.

        실제 대화 1:
        A: ...
        B: ...

        실제 대화 2:
        A: ...
        B: ..."

        Question: {question}

        Answer: {answer}
        """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an English teacher. "
                    "Return valid JSON only."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()

    try:
        result = json.loads(content)

    except Exception:
        return None

    if not result.get("has_candidate"):
        return None

    return result
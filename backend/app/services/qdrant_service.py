import os
import uuid
from typing import Optional

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://118.32.56.158:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "gptictionary_questions")

client = QdrantClient(url=QDRANT_URL)


def save_question_to_qdrant(
    question: str,
    answer: str,
    vector: list[float],
    question_id: Optional[int] = None,
) -> str:
    point_id = str(uuid.uuid4())

    payload = {
        "question": question,
        "answer": answer,
    }

    if question_id is not None:
        payload["question_id"] = question_id

    client.upsert(
        collection_name=QDRANT_COLLECTION,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload=payload,
            )
        ],
    )

    return point_id


def search_similar_questions(vector: list[float], limit: int = 5):
    result = client.query_points(
        collection_name=QDRANT_COLLECTION,
        query=vector,
        limit=limit,
    )

    return result.points


def get_collections():
    return client.get_collections()
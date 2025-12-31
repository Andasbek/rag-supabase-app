import os
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

EMBEDDING_MODEL = os.environ.get("EMBEDDINGS_MODEL", "text-embedding-3-small")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")

def get_embedding(text: str) -> List[float]:
    """Generates embedding for a single string."""
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=EMBEDDING_MODEL).data[0].embedding

def generate_answer(question: str, context_chunks: List[str]) -> str:
    """Generates an answer using LLM based on context."""
    
    context_text = "\n\n".join(context_chunks)
    
    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant for a Question Answering system. "
                "Use the following pieces of retrieved context to answer the user's question. "
                "If the answer is not in the context, say that you don't know. "
                "Do not make up sources or information."
            )
        },
        {
            "role": "user",
            "content": f"Context:\n{context_text}\n\nQuestion: {question}"
        }
    ]

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        temperature=0.1
    )
    
    return response.choices[0].message.content

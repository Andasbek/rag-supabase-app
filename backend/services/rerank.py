from typing import List, Dict
import json
from openai import OpenAI
from backend.config import Config

client = OpenAI(api_key=Config.OPENAI_API_KEY)

def rerank(question: str, candidates: List[Dict], top_n: int = 5) -> List[Dict]:
    """
    Reranks a list of candidate chunks based on relevance to the question using an LLM.
    
    Args:
        question: The user's query.
        candidates: List of candidate dictionaries (must contain 'content').
        top_n: Number of top results to return.
        
    Returns:
        List[Dict]: Top N reranked candidates.
    """
    if not Config.RERANK_ENABLED:
        return candidates[:top_n]
        
    if not candidates:
        return []

    print(f"[Rerank] Reranking {len(candidates)} candidates for question: '{question}'")

    # Format candidates for LLM
    candidate_texts = []
    for i, c in enumerate(candidates):
        # Taking first 300 chars for preview to save tokens if needed, 
        # but for accuracy full content is better. Let's send full content but truncated reasonably if huge.
        content_preview = c.get("content", "")[:1000] 
        candidate_texts.append(f"ID: {i}\nContent: {content_preview}\n")
    
    candidates_block = "\n---\n".join(candidate_texts)
    
    prompt = f"""
    You are a relevance ranker. You will be given a QUESTION and a list of PASSAGES.
    Your task is to rank the passages based on how relevant they are to answering the question.
    
    Return a JSON object with a list of indices sorted by relevance (most relevant first).
    Format: {{ "ranked_indices": [2, 0, 1, ...] }}
    
    Only include indices of passages that are somewhat relevant. If a passage is completely irrelevant, exclude it.
    
    QUESTION: {question}
    
    PASSAGES:
    {candidates_block}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Use a faster/cheaper model for reranking if possible, or Config.LLM_MODEL
            messages=[
                {"role": "system", "content": "You are a helpful relevance ranking assistant. Output valid JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0
        )
        
        result_text = response.choices[0].message.content
        result_json = json.loads(result_text)
        ranked_indices = result_json.get("ranked_indices", [])
        
        # Reconstruct result list
        reranked_results = []
        for idx in ranked_indices:
            if 0 <= idx < len(candidates):
                item = candidates[idx]
                # We can add a flag or score if we want
                reranked_results.append(item)
                
        # Fill with remaining if we don't have enough (optional fallback)? 
        # The requirement says "graceful fallback: return candidates as is". 
        # But if LLM returns partial list, we probably trust it. 
        # Let's stick to the top N from the ranked list.
        
        print(f"[Rerank] Success. Returned {len(reranked_results[:top_n])} items.")
        return reranked_results[:top_n]
        
    except Exception as e:
        print(f"[Rerank] Error: {e}. Fallback to original order.")
        return candidates[:top_n]

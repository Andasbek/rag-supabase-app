# Project 11 Demo: Caching & Reranking

This guide helps you verify the Reranking and Caching features.

## Prerequisites
Ensure your `.env` has the following enabled:
```bash
RERANK_ENABLED=true
CACHE_ENABLED=true
```

## Step 1: Start the Backend
```bash
uvicorn backend.main:app --reload
```

## Step 2: Verification Scenario

### 1. First Request (Cache Miss + Rerank)
Send a question to the API (via Streamlit or cURL).
**Question:** "How do I upload a document?"

**Expected Logs:**
- `[CACHE MISS] key='how do i upload a document' ...`
- `--- Hybrid Search Mini-Report ---` (Top-K results)
- `[Rerank] Reranking 10 candidates...`
- `--- Rerank Mini-Report ---` (Top-N results, order might differ from search)
- `[TIMING] Total: ... | Retrieval: ... | Rerank: ... | Gen: ...`

### 2. Second Request (Cache Hit)
Send the **exact same question** again immediately.

**Expected Logs:**
- `[CACHE HIT] key='how do i upload a document' | Total: X.XXms`
- **No** Retrieval/Rerank logs.
- Response time should be significantly faster (e.g., < 1ms vs 2000ms).

### 3. Rerank Verification
Disable Cache (`CACHE_ENABLED=false`) temporarily or ask a different question.
Observe the "Before Rerank" (Retrieval Report) and "After Rerank" (Rerank Report) lists in the console. 
- You should see fewer items in the Rerank report (Top-N vs Top-K).
- The order of items may change based on LLM relevance scoring.

## Troubleshooting
- If **Reranking** fails, check logs for `[Rerank] Error`. It should fallback to original candidates.
- If **Cache** is not hitting, check if you changed the question or config between requests.

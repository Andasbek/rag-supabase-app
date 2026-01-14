import requests
import time
import json
import sys
import os

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    try:
        resp = requests.get(f"{BASE_URL}/health")
        if resp.status_code == 200:
            print("[OK] Health check passed.")
            return True
    except Exception as e:
        print(f"[ERR] Health check failed: {e}")
    return False

def test_upload():
    filename = "test_rerank_concept.txt"
    content = "Reranking helps improve search relevance by using an LLM to re-score candidates. Caching improves performance by storing results for repeated queries. LLM based rerankers are slower but more accurate."
    
    # Write dummy file
    with open(filename, "w") as f:
        f.write(content)
        
    try:
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "text/plain")}
            resp = requests.post(f"{BASE_URL}/documents/upload", files=files)
        
        if resp.status_code == 200:
            print("[OK] Uploaded test document. Waiting 5s for indexing...")
            time.sleep(5) # Allow background indexing to complete
            return True
        else:
            print(f"[ERR] Upload failed: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
         print(f"[ERR] Upload exception: {e}")
         return False
    finally:
        if os.path.exists(filename):
            os.remove(filename)

def test_chat(question, source_ids=None):
    payload = {
        "question": question,
        "source_ids": source_ids or []
    }
    start = time.perf_counter()
    try:
        resp = requests.post(f"{BASE_URL}/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()
        duration = (time.perf_counter() - start) * 1000
        print(f"Request '{question}' took {duration:.2f}ms")
        return data, duration
    except Exception as e:
        print(f"[ERR] Chat request failed: {e}")
        return None, 0

def run_verification():
    print("Waiting for server to be ready...")
    for _ in range(10):
        if test_health():
            break
        time.sleep(1)
    else:
        print("Server not ready. Exiting.")
        sys.exit(1)

    print("\n--- TEST 0: Seed Data ---")
    if not test_upload():
        print("Skipping tests due to upload failure (DB might be down or not configured).")
        # Proceed anyway to test empty cache behvaiour? No, we saw that fails.
        sys.exit(1)

    print("\n--- TEST 1: Cache Miss + Rerank (Expected: High Latency) ---")
    question = "How does reranking work?" 
    
    resp1, duration1 = test_chat(question)
    
    print("\n--- TEST 2: Cache Hit (Expected: Low Latency) ---")
    # Exact same question
    resp2, duration2 = test_chat(question)

    print(f"\nTime Difference: First={duration1:.2f}ms vs Second={duration2:.2f}ms")
    if duration2 < duration1 and duration2 < 100: 
        print("[SUCCESS] Cache Hit Verified.")
    else:
        print("[WARNING] Cache might not have hit, or system is slow.")

    print("\nCheck the SERVER LOGS for '[CACHE MISS]', 'Mini-Report', and '[CACHE HIT]'.")

if __name__ == "__main__":
    run_verification()

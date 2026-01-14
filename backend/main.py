from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from typing import List, Dict, Any
import uuid
import asyncio
import time
from backend.services.storage import get_supabase_client
from backend.services.ingestion import process_document
from backend.services.llm import get_embedding, generate_answer
from backend.services.rerank import rerank
from backend.services.cache import chat_cache
from backend.config import Config
from backend.models import SourceResponse, ChatRequest, ChatResponse, Source

app = FastAPI(title="Docs Q&A RAG API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/documents/upload", response_model=SourceResponse)
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    supabase = get_supabase_client()
    
    # Read file content
    content = await file.read()
    
    # Create source record
    data = {
        "filename": file.filename,
        "filetype": file.content_type,
        "status": "uploaded"
    }
    
    response = supabase.table("sources").insert(data).execute()
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create source record")
    
    source_record = response.data[0]
    source_id = source_record["id"]
    
    # Trigger background indexing
    background_tasks.add_task(process_document, source_id, content, file.filename)
    
    return source_record

@app.get("/documents", response_model=List[SourceResponse])
def get_documents():
    supabase = get_supabase_client()
    response = supabase.table("sources").select("*").order("created_at", desc=True).execute()
    return response.data

@app.delete("/documents/{source_id}")
def delete_document(source_id: uuid.UUID):
    supabase = get_supabase_client()
    # Cascading delete in SQL should handle chunks
    response = supabase.table("sources").delete().eq("id", str(source_id)).execute()
    if not response.data:
         # It might return empty list if already deleted or not found, but trying to be robust
         pass
    return {"message": "Deleted"}

def rrf_fusion(semantic_list: List[Dict], keyword_list: List[Dict], k: int = 60) -> List[Dict]:
    """
    Reciprocal Rank Fusion (RRF) algorithm.
    """
    fused_scores = {}
    
    # Process semantic results
    for rank, item in enumerate(semantic_list):
        key = (item["source_id"], item["chunk_index"])
        if key not in fused_scores:
            fused_scores[key] = {"item": item, "score": 0.0}
        fused_scores[key]["score"] += 1 / (rank + k)
        
    # Process keyword results
    for rank, item in enumerate(keyword_list):
        key = (item["source_id"], item["chunk_index"])
        if key not in fused_scores:
            fused_scores[key] = {"item": item, "score": 0.0}
        fused_scores[key]["score"] += 1 / (rank + k)
    
    # Sort by fused score descending
    sorted_fused = sorted(fused_scores.values(), key=lambda x: x["score"], reverse=True)
    
    # Return the original item with updated score (mapped to similarity for compatibility)
    result = []
    for entry in sorted_fused:
        item = entry["item"]
        item["similarity"] = entry["score"] # Overwrite similarity with RRF score
        result.append(item)
        
    return result

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    t0 = time.perf_counter()
    
    # 1. Check Cache
    source_ids_str = [str(uid) for uid in request.source_ids] if request.source_ids else []
    cached_response = chat_cache.get(request.question, source_ids_str)
    
    if cached_response:
        t_total = (time.perf_counter() - t0) * 1000
        print(f"\n[CACHE HIT] key='{request.question}' | Total: {t_total:.2f}ms")
        return cached_response
    
    print(f"\n[CACHE MISS] key='{request.question}' - Proceeding to retrieval...")
    
    t_retrieval_start = time.perf_counter()
    supabase = get_supabase_client()
    
    # 2. Embed query
    query_embedding = get_embedding(request.question)
    
    # 3. Parallel Search Execution (Semantic + Keyword)
    filter_ids = source_ids_str if source_ids_str else None
    
    # Semantic Search Params
    semantic_params = {
        "query_embedding": query_embedding,
        "match_threshold": 0.3, 
        "match_count": Config.RETRIEVAL_TOP_K * 2, # Fetch more for fusion
        "filter_source_ids": filter_ids
    }
    
    # Keyword Search Params
    keyword_params = {
        "query_text": request.question,
        "match_count": Config.RETRIEVAL_TOP_K * 2,
        "filter_source_ids": filter_ids
    }

    # Execute in parallel
    task_semantic = asyncio.to_thread(lambda: supabase.rpc("match_chunks", semantic_params).execute())
    task_keyword = asyncio.to_thread(lambda: supabase.rpc("match_chunks_keyword", keyword_params).execute())

    results = await asyncio.gather(task_semantic, task_keyword, return_exceptions=True)
    
    # Handle results
    semantic_res = results[0]
    keyword_res = results[1]
    
    semantic_matches = semantic_res.data if not isinstance(semantic_res, Exception) and semantic_res.data else []
    keyword_matches = keyword_res.data if not isinstance(keyword_res, Exception) and keyword_res.data else []
    
    if isinstance(semantic_res, Exception):
        print(f"Error in Semantic Search: {semantic_res}")
    if isinstance(keyword_res, Exception):
        print(f"Error in Keyword Search: {keyword_res}")

    # 4. RRF Fusion
    fused_matches = rrf_fusion(semantic_matches, keyword_matches, k=60)
    retrieval_candidates = fused_matches[:Config.RETRIEVAL_TOP_K]
    
    t_retrieval_end = time.perf_counter()
    t_retrieval_ms = (t_retrieval_end - t_retrieval_start) * 1000
    
    # Log Retrieval Results
    print("\n--- Retrieval Mini-Report ---")
    print(f"Top-{Config.RETRIEVAL_TOP_K} candidates after RRF:")
    for i, m in enumerate(retrieval_candidates[:5]):
        print(f"{i+1}. ID: {m.get('source_id')} | Chunk: {m.get('chunk_index')} | Score: {m.get('similarity'):.4f}")

    # 5. Rerank
    t_rerank_start = time.perf_counter()
    
    reranked_candidates = rerank(request.question, retrieval_candidates, top_n=Config.RERANK_TOP_N)
    
    t_rerank_end = time.perf_counter()
    t_rerank_ms = (t_rerank_end - t_rerank_start) * 1000

    # Log Rerank Results
    if Config.RERANK_ENABLED:
        print("\n--- Rerank Mini-Report ---")
        print(f"Top-{Config.RERANK_TOP_N} candidates after Rerank:")
        for i, m in enumerate(reranked_candidates):
            print(f"{i+1}. ID: {m.get('source_id')} | Chunk: {m.get('chunk_index')} | Content Preview: {m.get('content')[:50]}...")

    # 6. Generate Answer
    t_gen_start = time.perf_counter()
    
    if not reranked_candidates:
        chat_response = ChatResponse(
            answer="I couldn't find any relevant information via Semantic or Keyword search.",
            sources=[]
        )
    else:
        context_chunks = [match["content"] for match in reranked_candidates]
        answer = generate_answer(request.question, context_chunks)
        
        # Format Sources
        source_ids = list(set([m["source_id"] for m in reranked_candidates]))
        filename_map = {}
        if source_ids:
            try:
                src_res = await asyncio.to_thread(lambda: supabase.table("sources").select("id, filename").in_("id", source_ids).execute())
                filename_map = {item["id"]: item["filename"] for item in src_res.data}
            except Exception as e:
                print(f"Error fetching filenames: {e}")

        final_sources = []
        for m in reranked_candidates:
            final_sources.append(Source(
                source_id=m["source_id"],
                filename=filename_map.get(m["source_id"], "Unknown"),
                chunk_index=m["chunk_index"],
                similarity=m["similarity"],
                chunk_text=m["content"]
            ))
            
        chat_response = ChatResponse(
            answer=answer,
            sources=final_sources
        )

    t_gen_end = time.perf_counter()
    t_gen_ms = (t_gen_end - t_gen_start) * 1000
    t_total = (t_gen_end - t0) * 1000
    
    # 7. Set Cache
    if reranked_candidates:
        chat_cache.set(request.question, chat_response, source_ids_str)
        
    # Final Config/Timing Log
    print(f"\n[TIMING] Total: {t_total:.2f}ms | Retrieval: {t_retrieval_ms:.2f}ms | Rerank: {t_rerank_ms:.2f}ms | Gen: {t_gen_ms:.2f}ms")
    print(f"[STATS] Cache Hits: {chat_cache.hits} | Misses: {chat_cache.misses}")
    
    return chat_response

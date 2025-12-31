from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from typing import List
import uuid
from backend.services.storage import get_supabase_client
from backend.services.ingestion import process_document
from backend.services.llm import get_embedding, generate_answer
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

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    supabase = get_supabase_client()
    
    # 1. Embed query
    query_embedding = get_embedding(request.question)
    
    # 2. Vector Search (RPC)
    # Ensure source_ids are converted to strings if they exist, or passed as None
    filter_ids = [str(uid) for uid in request.source_ids] if request.source_ids else None
    
    rpc_params = {
        "query_embedding": query_embedding,
        "match_threshold": 0.3, # Lowered from 0.5 to catch more context
        "match_count": 5,
        "filter_source_ids": filter_ids
    }
    
    response = supabase.rpc("match_chunks", rpc_params).execute()
    matches = response.data
    
    # Debug Logging
    print(f"Query: {request.question}")
    print(f"Found {len(matches)} matches.")
    if matches:
        print(f"Top match similarity: {matches[0].get('similarity', 0)}")
        print(f"Top match content snippet: {matches[0].get('content', '')[:100]}...")

    
    # 3. Generate Answer
    if not matches:
        return ChatResponse(
            answer="I couldn't find any relevant information in the uploaded documents to answer your question.",
            sources=[]
        )
    
    context_chunks = [match["content"] for match in matches]
    answer = generate_answer(request.question, context_chunks)
    
    # 4. Format Layout
    # Join with sources table to get filenames? 
    # The RPC returns source_id. We can fetch filenames or if RPC matched joined we'd have it. 
    # For optimization, we can fetch filenames for the distinct source_ids in matches.
    
    source_ids = list(set([m["source_id"] for m in matches]))
    if source_ids:
        src_res = supabase.table("sources").select("id, filename").in_("id", source_ids).execute()
        filename_map = {item["id"]: item["filename"] for item in src_res.data}
    else:
        filename_map = {}

    final_sources = []
    for m in matches:
        final_sources.append(Source(
            source_id=m["source_id"],
            filename=filename_map.get(m["source_id"], "Unknown"),
            chunk_index=m["chunk_index"],
            similarity=m["similarity"],
            chunk_text=m["content"]
        ))
        
    return ChatResponse(
        answer=answer,
        sources=final_sources
    )

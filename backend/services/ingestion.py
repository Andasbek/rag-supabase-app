import io
import uuid
from typing import List
from pypdf import PdfReader
from backend.services.llm import get_embedding
from backend.services.storage import get_supabase_client

CHUNK_SIZE = 1000  # Characters
OVERLAP = 200

def extract_text(file_content: bytes, filename: str) -> str:
    """Extracts text from TXT or PDF files."""
    if filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(file_content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    else:
        # Assume text-based
        return file_content.decode("utf-8")

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> List[str]:
    """Splits text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

async def process_document(source_id: str, file_content: bytes, filename: str):
    """Background task to process document: extract -> chunk -> embed -> store."""
    supabase = get_supabase_client()
    
    try:
        # Update status to indexing
        supabase.table("sources").update({"status": "indexing"}).eq("id", source_id).execute()
        
        # 1. Extract
        text = extract_text(file_content, filename)
        
        # 2. Chunk
        text_chunks = chunk_text(text)
        
        # 3. Embed & Store
        # We can batch this if needed, but for simplicity loop or small batches
        records = []
        for i, chunk in enumerate(text_chunks):
            embedding = get_embedding(chunk)
            records.append({
                "source_id": source_id,
                "chunk_index": i,
                "content": chunk,
                "embedding": embedding
            })
            
        # Bulk insert chunks
        # Supabase/Postgres limits might apply to payload size, doing in batches of 50 is safer ideally
        batch_size = 50
        for i in range(0, len(records), batch_size):
            supabase.table("chunks").insert(records[i:i+batch_size]).execute()
            
        # Update status to indexed
        supabase.table("sources").update({"status": "indexed"}).eq("id", source_id).execute()
        print(f"Successfully indexed {filename} ({source_id})")

    except Exception as e:
        print(f"Error indexing {filename}: {e}")
        supabase.table("sources").update({"status": "failed", "error": str(e)}).eq("id", source_id).execute()

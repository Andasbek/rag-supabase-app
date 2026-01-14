-- Enable the pg_trgm extension for fuzzy matching (optional but good for specific searches, strictly we use FTS here)
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 1. Create a GIN index on chunks.content for fast English full-text search
CREATE INDEX IF NOT EXISTS idx_chunks_content_fts ON chunks USING gin (to_tsvector('english', content));

-- 2. Create RPC function for Keyword Search
create or replace function match_chunks_keyword (
  query_text text,
  match_count int,
  filter_source_ids uuid[] default null
)
returns table (
  id uuid,
  source_id uuid,
  chunk_index int,
  content text,
  similarity float -- Reusing 'similarity' field name for rank/score to match match_chunks interface roughly or for simplicity
)
language plpgsql
as $$
begin
  return query
  select
    c.id,
    c.source_id,
    c.chunk_index,
    c.content,
    ts_rank(to_tsvector('english', c.content), websearch_to_tsquery('english', query_text))::float as similarity
  from chunks c
  where to_tsvector('english', c.content) @@ websearch_to_tsquery('english', query_text)
  and (filter_source_ids is null or c.source_id = any(filter_source_ids))
  order by similarity desc
  limit match_count;
end;
$$;

-- Create a function to search for similar chunks
create or replace function match_chunks (
  query_embedding vector(1536),
  match_threshold float,
  match_count int,
  filter_source_ids uuid[] default null
)
returns table (
  id uuid,
  source_id uuid,
  chunk_index int,
  content text,
  similarity float
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
    1 - (c.embedding <=> query_embedding) as similarity
  from chunks c
  where 1 - (c.embedding <=> query_embedding) > match_threshold
  and (filter_source_ids is null or c.source_id = any(filter_source_ids))
  order by c.embedding <=> query_embedding
  limit match_count;
end;
$$;

-- Enable the pgvector extension to work with embedding vectors
create extension if not exists vector;

-- Create a table to store document sources
create table if not exists sources (
  id uuid primary key default gen_random_uuid(),
  filename text not null,
  filetype text not null,
  status text not null default 'uploaded', -- uploaded, indexing, indexed, failed
  error text,
  created_at timestamptz default now()
);

-- Create a table to store text chunks and their embeddings
create table if not exists chunks (
  id uuid primary key default gen_random_uuid(),
  source_id uuid references sources(id) on delete cascade not null,
  chunk_index int not null,
  content text not null,
  embedding vector(1536), -- Dimension for OpenAI text-embedding-3-small
  created_at timestamptz default now()
);

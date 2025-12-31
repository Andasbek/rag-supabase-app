import streamlit as st
import requests
import os

# Backend API URL
API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Docs Q&A RAG", layout="wide")

st.title("Docs Q&A RAG Application")

# --- SIDEBAR: Manage Documents ---
with st.sidebar:
    st.header("Manage Documents")
    
    # Upload Section
    st.subheader("Upload New Document")
    uploaded_file = st.file_uploader("Choose a TXT or PDF file", type=["txt", "pdf"])
    
    if uploaded_file is not None:
        if st.button("Upload & Index"):
            with st.spinner("Uploading and indexing..."):
                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                try:
                    response = requests.post(f"{API_URL}/documents/upload", files=files)
                    if response.status_code == 200:
                        st.success(f"Successfully uploaded {uploaded_file.name}")
                        st.rerun()
                    else:
                        st.error(f"Upload failed: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")

    st.divider()
    
    # List Section
    st.subheader("Uploaded Documents")
    if st.button("Refresh List"):
        st.rerun()
        
    documents = []
    try:
        response = requests.get(f"{API_URL}/documents")
        if response.status_code == 200:
            documents = response.json()
            if documents:
                for doc in documents:
                    with st.expander(f"{doc['filename']} ({doc['status']})"):
                        st.write(f"**ID:** {doc['id']}")
                        st.write(f"**Created:** {doc['created_at']}")
                        if doc.get("error"):
                            st.error(f"Error: {doc['error']}")
                        
                        if st.button("Delete", key=doc['id']):
                            res = requests.delete(f"{API_URL}/documents/{doc['id']}")
                            if res.status_code == 200:
                                st.success("Deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete")
            else:
                st.info("No documents uploaded yet.")
        else:
            st.error("Failed to fetch documents.")
    except Exception as e:
        st.error(f"Error fetching documents: {e}")

# --- MAIN AREA: CHAT ---

# Document Filtering
available_docs = {doc['filename']: doc['id'] for doc in documents} if documents else {}
selected_filenames = st.multiselect(
    "Filter by Documents (Optional)", 
    options=list(available_docs.keys()),
    help="Select specific documents to search. If empty, searches all."
)
selected_source_ids = [available_docs[name] for name in selected_filenames]

st.divider()

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Clear Chat Button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()

# Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message:
            with st.expander("View Sources"):
                for src in message["sources"]:
                    st.markdown(f"**{src['filename']}** (Similarity: {src['similarity']:.2f})")
                    st.text(src['chunk_text'])

# Chat Input
if prompt := st.chat_input("Ask a question based on your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                payload = {
                    "question": prompt,
                    "source_ids": selected_source_ids if selected_source_ids else None
                }
                
                res = requests.post(f"{API_URL}/chat", json=payload)
                
                if res.status_code == 200:
                    data = res.json()
                    answer = data["answer"]
                    sources = data["sources"]
                    
                    st.markdown(answer)
                    with st.expander("View Sources"):
                            for src in sources:
                                st.markdown(f"**{src['filename']}** (Similarity: {src['similarity']:.2f})")
                                st.text(src['chunk_text'])
                    
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": answer,
                        "sources": sources
                    })
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"Connection error: {e}")


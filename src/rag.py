import os
import glob
import math
import streamlit as st
import PyPDF2
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Setup API Key
API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
if API_KEY:
    genai.configure(api_key=API_KEY)

# ----------------- Text Extraction & Chunking -----------------

def extract_text_from_pdf(pdf_file):
    """Extracts all text from a PDF file stream using PyPDF2."""
    text = ""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        return f"Error reading PDF: {e}"
    return text.strip()

def chunk_text(text, chunk_size=1000, chunk_overlap=200):
    """Splits text into chunks of roughly chunk_size characters, respecting word boundaries."""
    if not text:
        return []
    
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if current_length >= chunk_size:
            chunks.append(" ".join(current_chunk))
            # Keep about 20% overlap
            overlap_count = max(1, len(current_chunk) // 5)
            current_chunk = current_chunk[-overlap_count:]
            current_length = sum(len(w) + 1 for w in current_chunk)
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

# ----------------- Embedding Generation -----------------

def get_embeddings(texts, is_query=False):
    """Generates embeddings using Google's text-embedding-004 model. Falls back to embedding-001 if needed."""
    api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")
    genai.configure(api_key=api_key)
    
    task_type = "retrieval_query" if is_query else "retrieval_document"
    
    is_single = isinstance(texts, str)
    if is_single:
        texts = [texts]
        
    try:
        response = genai.embed_content(
            model="models/gemini-embedding-001",
            content=texts,
            task_type=task_type
        )
        embeddings = response.get("embedding", [])
        return embeddings[0] if is_single and embeddings else embeddings
    except Exception as e:
        try:
            # Fallback to gemini-embedding-2
            response = genai.embed_content(
                model="models/gemini-embedding-2",
                content=texts,
                task_type=task_type
            )
            embeddings = response.get("embedding", [])
            return embeddings[0] if is_single and embeddings else embeddings
        except Exception as e2:
            raise RuntimeError(f"Embedding API error: {e2}")

# ----------------- In-Memory Vector Store Fallback -----------------

def cosine_similarity(v1, v2):
    """Computes cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

def simple_text_search(query, documents, n_results=5):
    """Basic keyword overlap search if embeddings fail."""
    query_words = set(query.lower().split())
    scored_docs = []
    for doc in documents:
        doc_words = set(doc["text"].lower().split())
        match_count = len(query_words.intersection(doc_words))
        scored_docs.append((match_count, doc))
        
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    top_docs = scored_docs[:n_results]
    
    return {
        "documents": [[doc["text"] for _, doc in top_docs]],
        "metadatas": [[doc["metadata"] for _, doc in top_docs]],
        "distances": [[1.0 / (score + 1.0) for score, _ in top_docs]]
    }

class InMemoryStore:
    def __init__(self):
        self.documents = []
        
    def add_documents(self, texts, embeddings, metadatas=None):
        if metadatas is None:
            metadatas = [{} for _ in texts]
        # Embeddings can be None if generation failed
        embs = embeddings if embeddings is not None else [None] * len(texts)
        for t, emb, meta in zip(texts, embs, metadatas):
            self.documents.append({
                "text": t,
                "embedding": emb,
                "metadata": meta
            })
            
    def query(self, query_embedding, n_results=5):
        scored_docs = []
        for doc in self.documents:
            # If some doc lacks embedding, skip cosine similarity and assign 0
            if doc["embedding"] is None or query_embedding is None:
                score = 0.0
            else:
                score = cosine_similarity(query_embedding, doc["embedding"])
            scored_docs.append((score, doc))
            
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_docs = scored_docs[:n_results]
        
        return {
            "documents": [[doc["text"] for _, doc in top_docs]],
            "metadatas": [[doc["metadata"] for _, doc in top_docs]],
            "distances": [[1.0 - score for score, _ in top_docs]]
        }

# ----------------- Unified Vector Store Wrapper -----------------

class RAGVectorStore:
    def __init__(self):
        self.use_chroma = False
        self.chroma_client = None
        self.collection = None
        self.in_memory_store = InMemoryStore()
        
        try:
            import chromadb
            # Initialize persistent client in workspace
            self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
            self.collection = self.chroma_client.get_or_create_collection("career_assistant")
            self.use_chroma = True
        except Exception as e:
            self.use_chroma = False
            
    def add_documents(self, texts, embeddings, metadatas=None):
        if not texts:
            return
        if metadatas is None:
            metadatas = [{} for _ in texts]
            
        if self.use_chroma and embeddings is not None:
            try:
                import uuid
                ids = [str(uuid.uuid4()) for _ in texts]
                self.collection.add(
                    documents=texts,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    ids=ids
                )
                return
            except Exception as e:
                # If chroma add fails, fallback to in-memory store
                pass
                
        self.in_memory_store.add_documents(texts, embeddings, metadatas)
        
    def query(self, query_text, query_embedding, n_results=5):
        if self.use_chroma and query_embedding is not None:
            try:
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results
                )
                if results and results.get("documents") and len(results["documents"][0]) > 0:
                    return results
            except Exception as e:
                pass
                
        # Fallback to InMemoryStore
        if query_embedding is not None:
            return self.in_memory_store.query(query_embedding, n_results)
        else:
            # Word-based matching if embeddings are completely missing
            all_docs = []
            if self.use_chroma:
                try:
                    all_data = self.collection.get()
                    if all_data and all_data.get("documents"):
                        for doc, meta in zip(all_data["documents"], all_data["metadatas"] or [{}]):
                            all_docs.append({"text": doc, "metadata": meta})
                except Exception:
                    pass
            if not all_docs:
                all_docs = self.in_memory_store.documents
            return simple_text_search(query_text, all_docs, n_results)
            
    def delete_resume_chunks(self):
        if self.use_chroma:
            try:
                self.collection.delete(where={"source_type": "resume"})
            except Exception:
                pass
        self.in_memory_store.documents = [
            doc for doc in self.in_memory_store.documents
            if doc["metadata"].get("source_type") != "resume"
        ]

# ----------------- Initialization & Processing -----------------

def initialize_rag():
    """Initializes vector store and loads career documents from documents/ folder."""
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = RAGVectorStore()
    if "processed_documents" not in st.session_state:
        st.session_state.processed_documents = set()
        
    os.makedirs("documents", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    
    # List PDF files in documents/
    pdf_files = glob.glob(os.path.join("documents", "*.pdf"))
    
    # Process each PDF if not already loaded
    new_files = [f for f in pdf_files if f not in st.session_state.processed_documents]
    for file_path in new_files:
        try:
            with open(file_path, "rb") as f:
                text = extract_text_from_pdf(f)
            if text and not text.startswith("Error"):
                chunks = chunk_text(text)
                if chunks:
                    filename = os.path.basename(file_path).lower()
                    source_type = "career_guide"
                    if "interview" in filename:
                        source_type = "interview_guide"
                    elif "resume" in filename:
                        source_type = "resume"
                        
                    metadatas = [{
                        "source_file": os.path.basename(file_path),
                        "source_type": source_type,
                        "chunk_index": i
                    } for i in range(len(chunks))]
                    
                    embeddings = None
                    try:
                        embeddings = get_embeddings(chunks)
                    except Exception as e:
                        # Friendly message instead of crashing
                        st.sidebar.warning(f"⚠️ Embeddings failed for {os.path.basename(file_path)}. Using text search.")
                        
                    st.session_state.vector_store.add_documents(chunks, embeddings, metadatas)
                    st.session_state.processed_documents.add(file_path)
        except Exception as e:
            # Never crash
            st.sidebar.error(f"Error loading {os.path.basename(file_path)}: {e}")

def process_uploaded_resume(uploaded_file):
    """Saves resume to uploads/, extracts text, chunks it, embeds, and adds to store."""
    if uploaded_file is None:
        return None
        
    try:
        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", uploaded_file.name)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        # Extract text
        with open(file_path, "rb") as f:
            text = extract_text_from_pdf(f)
            
        if not text or text.startswith("Error"):
            return "Error extracting text from resume PDF"
            
        chunks = chunk_text(text)
        if not chunks:
            return "No text chunks found in resume"
            
        # Embeddings
        embeddings = None
        try:
            embeddings = get_embeddings(chunks)
        except Exception as e:
            st.sidebar.warning(f"⚠️ Embeddings failed for resume. Using text search.")
            
        if "vector_store" not in st.session_state:
            st.session_state.vector_store = RAGVectorStore()
            
        # Delete old resume chunks
        st.session_state.vector_store.delete_resume_chunks()
        
        # Add new chunks
        metadatas = [{
            "source_file": uploaded_file.name,
            "source_type": "resume",
            "chunk_index": i
        } for i in range(len(chunks))]
        
        st.session_state.vector_store.add_documents(chunks, embeddings, metadatas)
        
        # Save raw text to session state
        st.session_state.resume_text = text
        return text
    except Exception as e:
        return f"Error processing resume: {e}"

def retrieve_context(user_question, n_results=5):
    """Retrieves relevant chunks from the vector store."""
    if "vector_store" not in st.session_state:
        return ""
        
    query_embedding = None
    try:
        query_embedding = get_embeddings(user_question, is_query=True)
    except Exception:
        pass
        
    results = st.session_state.vector_store.query(user_question, query_embedding, n_results=n_results)
    
    if not results or not results.get("documents") or not results["documents"][0]:
        return ""
        
    formatted_context = []
    documents = results["documents"][0]
    metadatas = results.get("metadatas", [[]])[0]
    
    for doc, meta in zip(documents, metadatas):
        src_file = meta.get("source_file", "unknown")
        src_type = meta.get("source_type", "unknown")
        formatted_context.append(f"[{src_type.upper()} from {src_file}]:\n{doc}")
        
    return "\n\n---\n\n".join(formatted_context)

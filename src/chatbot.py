import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def career_chat(user_question):
    """
    Given a user question, retrieves relevant context from RAG,
    prompts Gemini, and returns a concise professional response.
    """
    try:
        from src.rag import retrieve_context
        # Retrieve relevant chunks from vector store
        context = retrieve_context(user_question, n_results=5)
        
        # Get raw resume text from session state if available
        resume_text = st.session_state.get("resume_text", "Not uploaded")
        
        # Configure API key
        api_key = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
        if not api_key:
            return "API Key not configured. Please set GEMINI_API_KEY in your secrets or environment variables."
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3.5-flash")
        
        prompt = f"""
You are an expert AI Career Assistant and professional career coach.
Your job is to answer the user's career, job search, resume, or interview question using the retrieved context from their resume and career/interview guides.

### Context
#### Resume
{resume_text[:3000] if resume_text != "Not uploaded" else "No resume uploaded."}

#### Retrieved Knowledge Chunks (Career/Interview Guides and Resume snippets)
{context if context else "No relevant career guide context found."}

### User Question
{user_question}

### Instructions
1. Provide a professional, encouraging, and highly actionable response.
2. Structure your answer using clean Markdown (bullet points, bold text, headings).
3. If the context does not contain enough information to answer the question fully, use your general career coaching knowledge but prioritize the provided context.
4. Keep the answer concise, clear, and professional.
"""
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"An error occurred while generating the response: {e}"

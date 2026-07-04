import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Read from Streamlit Secrets first, then .env
API_KEY = st.secrets.get("RAPIDAPI_KEY", os.getenv("RAPIDAPI_KEY"))
API_HOST = st.secrets.get("RAPIDAPI_HOST", os.getenv("RAPIDAPI_HOST", "jsearch-mega.p.rapidapi.com"))


def search_jobs(query):
    url = "https://jsearch-mega.p.rapidapi.com/search"

    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }

    params = {
        "query": query,
        "page": 1,
        "num_pages": 1,
        "country": "india"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        return data.get("data", [])

    except Exception as e:
        st.error(f"API Error: {e}")
        return []
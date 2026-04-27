import os


def get_secret(key):
    """Return secret from st.secrets (Streamlit Cloud) or os.getenv (local .env)."""
    try:
        import streamlit as st
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

import json
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from agent.embeddings import get_embedding_model, build_product_embeddings, build_customer_embeddings
from agent.tools import create_tools
from agent.agent_core import build_agent, invoke_agent
from agent.prompts import SYSTEM_PROMPT


@st.cache_resource
def _load_embedding_model():
    return get_embedding_model()


@st.cache_resource
def _build_product_emb(_df_product, _model):
    return build_product_embeddings(_df_product, _model)


@st.cache_resource
def _build_customer_emb(_df_customers, _model):
    return build_customer_embeddings(_df_customers, _model)

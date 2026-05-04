from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from config import get_secret

# Ordered most desired → least desired
MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
    "meta-llama/llama-4-scout-17b-16e-instruct"
]


def build_agent(tools, system_prompt, model=MODELS[0]):
    llm = ChatGroq(
        model=model,
        temperature=0.1,
        api_key=get_secret("GROQ_API_KEY"),
    )
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
    )
    return agent


def invoke_agent(agent, messages):
    result = agent.invoke({"messages": messages})
    return result["messages"]

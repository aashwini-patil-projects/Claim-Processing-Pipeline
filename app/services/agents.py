from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage
import os

def get_llm():
    """Lazy initialization of LLM"""
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    )

async def process_with_agent(content: str, task: str) -> str:
    """
    Generic agent processing function (not currently used in main workflow).
    Kept for reference or future use.
    """
    llm = get_llm()
    message = HumanMessage(content=f"{task}: {content}")
    response = await llm.agenerate([[message]])
    return response.generations[0][0].text

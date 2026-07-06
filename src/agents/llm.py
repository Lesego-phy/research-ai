# Centralized file to initialize Azure OpenAI model

from langchain_openai import AzureChatOpenAI
from src.config import settings

# This single instance will be shared across all our agents
azure_llm = AzureChatOpenAI(
    azure_deployment=settings.AZURE_OPENAI_DEPLOYMENT,
    api_version=settings.AZURE_OPENAI_API_VERSION,
    temperature=settings.LLM_TEMPERATURE,
)
# This file safely loads your environment variables so we don't have to repeat os.getenv() everywhere.
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    #Azure OpenAI Settings
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_DEPLOYMENT: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
    
    # Tavily Settings
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY")
    
    # Default LLM settings
    LLM_TEMPERATURE: float = 0.1

settings = Settings()
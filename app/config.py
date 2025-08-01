"""
Configuration settings for GenAI Chatbot
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings"""
    
    # API Settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_MAX_TOKENS: int = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    # Vector Database Settings
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./data/vector_db")
    CHROMA_PERSIST_DIRECTORY: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma")
    
    # MLflow Settings
    MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    MLFLOW_EXPERIMENT_NAME: str = os.getenv("MLFLOW_EXPERIMENT_NAME", "genai-chatbot")
    
    # Monitoring Settings
    PROMETHEUS_ENABLED: bool = os.getenv("PROMETHEUS_ENABLED", "True").lower() == "true"
    
    # RAG Settings
    RAG_TOP_K: int = int(os.getenv("RAG_TOP_K", "5"))
    RAG_SIMILARITY_THRESHOLD: float = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.7"))
    
    # Intent Classification Settings
    INTENT_CONFIDENCE_THRESHOLD: float = float(os.getenv("INTENT_CONFIDENCE_THRESHOLD", "0.8"))
    
    @classmethod
    def validate(cls) -> None:
        """Validate required settings"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        # Create data directories if they don't exist
        os.makedirs(cls.VECTOR_DB_PATH, exist_ok=True)
        os.makedirs(cls.CHROMA_PERSIST_DIRECTORY, exist_ok=True)

# Global settings instance
settings = Settings() 
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    HUGGINGFACE_API_TOKEN: str = ""
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    GROK_API_KEY: str = ""   # X.AI / Grok API key

    class Config:
        env_file = ".env"

settings = Settings()

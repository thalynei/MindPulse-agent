from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # 忽略.env中未定义的配置项
    )

    PROJECT_NAME: str = "MindPulse"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "AI增强型个人生产力工具"

    # 服务配置
    PORT: int = 8000

    # Ollama配置
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:1.5b"
    OLLAMA_ENABLED: bool = True
    OLLAMA_TIMEOUT: int = 30


settings = Settings()

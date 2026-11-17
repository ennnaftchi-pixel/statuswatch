from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_secret_key: str = "change-me"
    database_url: str = (
        "postgresql+asyncpg://statuswatch:statuswatch@db:5432/statuswatch"
    )
    admin_email: str = "admin@example.com"
    admin_password: str = "change-me"
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""


settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "dev"
    app_port: int = 8000
    owner_login: str = ""
    upstream_cache_ttl: int = 10
    upstream_timeout: int = 3
    dev_force_admin: bool = False

    reflexion_rondo_base_url: str = ""
    lck_pics_base_url: str = ""
    airflow_base_url: str = ""
    grafana_base_url: str = ""
    minio_base_url: str = ""
    reflexion_daemon_base_url: str = ""


settings = Settings()

from urllib.parse import quote_plus

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    user: str
    password: str
    host: str
    port: int
    name: str


class RabbitSettings(BaseModel):
    user: str
    password: str
    host: str
    port: int


class AuthSettings(BaseModel):
    api_key: str


class ApiSettings(BaseModel):
    port: int


class IdGeneratorSettings(BaseModel):
    node_id: int = Field(default=1, ge=0, le=1023)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__", extra="ignore")

    db: DatabaseSettings
    rabbit: RabbitSettings
    auth: AuthSettings
    api: ApiSettings
    id_generator: IdGeneratorSettings = Field(default_factory=IdGeneratorSettings)

    @property
    def database_url(self) -> str:
        user = quote_plus(self.db.user)
        password = quote_plus(self.db.password)
        name = quote_plus(self.db.name)
        return f"postgresql+asyncpg://{user}:{password}@{self.db.host}:{self.db.port}/{name}"

    @property
    def rabbitmq_url(self) -> str:
        user = quote_plus(self.rabbit.user)
        password = quote_plus(self.rabbit.password)
        return f"amqp://{user}:{password}@{self.rabbit.host}:{self.rabbit.port}/"


settings = Settings()

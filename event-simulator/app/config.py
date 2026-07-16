from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    service_name: str = Field('event-simulator', alias='SERVICE_NAME')
    kafka_bootstrap_servers: str = Field('localhost:9092', alias='KAFKA_BOOTSTRAP_SERVERS')
    event_topic: str = Field('events.unified.v1', alias='EVENT_TOPIC')
    transport: str = Field('memory', alias='SIMULATOR_TRANSPORT')
    api_port: int = Field(8900, alias='SIMULATOR_API_PORT')
    noise_ratio: float = Field(0.7, alias='SIMULATOR_NOISE_RATIO', ge=0, le=1)
    model_config = SettingsConfigDict(env_file='.env', extra='ignore', populate_by_name=True)


settings = Settings()

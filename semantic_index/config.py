from dataclasses import dataclass, field
from pathlib import Path
import yaml


@dataclass(frozen=True)
class EmbeddingFactoryConfig:
    batch_size: int = 32
    process_remote: bool = False
    remote_host: str = "http://localhost"
    remote_port: int = 8000
    remote_endpoint: str = "/encode"


@dataclass(frozen=True)
class DatabaseConfig:
    url: str = "sqlite:///semantic_index.db"
    echo: bool = False


@dataclass(frozen=True)
class Config:
    log_folder: str = "logs"
    log_level_console: str = "INFO"
    log_level_file: str = "DEBUG"
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    embedding_factory: EmbeddingFactoryConfig = field(
        default_factory=EmbeddingFactoryConfig
    )


def load_config(config_path: str | Path) -> Config:
    config_path = Path(config_path)
    if not config_path.exists():
        return Config()

    with open(config_path, "r", encoding="utf-8") as file:
        raw = yaml.safe_load(file) or {}

    return Config(
        log_folder=raw.get("log_folder", "logs"),
        log_level_console=raw.get("log_level_console", "INFO"),
        log_level_file=raw.get("log_level_file", "DEBUG"),
        database=DatabaseConfig(**raw.get("database", {})),
        embedding_factory=EmbeddingFactoryConfig(**raw.get("embedding_factory", {})),
    )


config = load_config("config.yaml")

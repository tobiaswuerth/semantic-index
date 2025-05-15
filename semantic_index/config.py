import yaml
from typing import NamedTuple


class EmbeddingFactoryConfig(NamedTuple):
    batch_size: int
    process_remote: bool
    remote_host: str
    remote_port: int
    remote_endpoint: str


class Config(NamedTuple):
    log_folder: str
    log_level_console: str
    log_level_file: str
    index_path: str
    embedding_factory: EmbeddingFactoryConfig


def load_config(config_path: str) -> Config:
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    config["embedding_factory"] = EmbeddingFactoryConfig(**config["embedding_factory"])
    return Config(**config)


config = load_config("config.yaml")

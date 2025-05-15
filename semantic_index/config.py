import yaml
from typing import NamedTuple


class Config(NamedTuple):
    log_folder: str
    log_level_console: str
    log_level_file: str
    index_path: str


def load_config(config_path: str) -> Config:
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    return Config(**config)


config = load_config("config.yaml")

from pathlib import Path

import yaml


def load_config(path="config.yaml"):
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    try:
        with config_path.open("r", encoding="utf-8") as config_file:
            return yaml.safe_load(config_file)
    except yaml.YAMLError as error:
        raise ValueError(f"Invalid YAML configuration: {path}") from error

from pathlib import Path

import yaml


def _raise_config_error(message):
    raise ValueError(f"Configuration error: {message}")


def _validate_mapping(value, path):
    if not isinstance(value, dict):
        _raise_config_error(f"{path} must be a dictionary")


def _validate_required(value, key, path):
    if key not in value:
        _raise_config_error(f"{path}.{key} is required")

    return value[key]


def _validate_non_empty_string(value, path):
    if not isinstance(value, str) or not value.strip():
        _raise_config_error(f"{path} must be a non-empty string")


def _validate_timeout(value, path):
    if not isinstance(value, int | float) or isinstance(value, bool):
        _raise_config_error(f"{path} must be a number")
    if value <= 0:
        _raise_config_error(f"{path} must be greater than 0")


def _validate_required_list(config, key):
    if key not in config:
        _raise_config_error(f"missing required key '{key}'")
    if not isinstance(config[key], list):
        _raise_config_error(f"{key} must be a list")

    return config[key]


def _validate_process(process, index):
    path = f"processes[{index}]"
    _validate_mapping(process, path)

    name = _validate_required(process, "name", path)
    _validate_non_empty_string(name, f"{path}.name")


def _validate_tcp_target(target, index):
    path = f"tcp[{index}]"
    _validate_mapping(target, path)

    host = _validate_required(target, "host", path)
    _validate_non_empty_string(host, f"{path}.host")

    port = _validate_required(target, "port", path)
    if not isinstance(port, int) or isinstance(port, bool):
        _raise_config_error(f"{path}.port must be an integer")
    if port < 1 or port > 65535:
        _raise_config_error(f"{path}.port must be between 1 and 65535")

    timeout = _validate_required(target, "timeout", path)
    _validate_timeout(timeout, f"{path}.timeout")


def _validate_http_target(target, index):
    path = f"http[{index}]"
    _validate_mapping(target, path)

    url = _validate_required(target, "url", path)
    _validate_non_empty_string(url, f"{path}.url")
    if not url.startswith(("http://", "https://")):
        _raise_config_error(f"{path}.url must start with http:// or https://")

    timeout = _validate_required(target, "timeout", path)
    _validate_timeout(timeout, f"{path}.timeout")


def validate_config(config):
    if not isinstance(config, dict):
        _raise_config_error("configuration must be a dictionary")

    processes = _validate_required_list(config, "processes")
    tcp_targets = _validate_required_list(config, "tcp")
    http_targets = _validate_required_list(config, "http")

    for index, process in enumerate(processes):
        _validate_process(process, index)

    for index, target in enumerate(tcp_targets):
        _validate_tcp_target(target, index)

    for index, target in enumerate(http_targets):
        _validate_http_target(target, index)


def load_config(path="config.yaml"):
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    try:
        with config_path.open("r", encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file)
    except yaml.YAMLError as error:
        raise ValueError(f"Invalid YAML configuration: {path}") from error

    validate_config(config)

    return config

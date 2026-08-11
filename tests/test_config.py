import pytest

from infrapulse.config import load_config, validate_config


def valid_config():
    return {
        "processes": [{"name": "explorer.exe"}],
        "tcp": [{"host": "localhost", "port": 80, "timeout": 2}],
        "http": [{"url": "https://httpbin.org/status/200", "timeout": 3}],
    }


def assert_config_error(config, expected_message):
    with pytest.raises(ValueError, match=expected_message):
        validate_config(config)


def test_validate_config_accepts_valid_configuration():
    validate_config(valid_config())


def test_validate_config_requires_dictionary():
    assert_config_error(
        None,
        "Configuration error: configuration must be a dictionary",
    )


def test_validate_config_requires_processes_key():
    config = valid_config()
    del config["processes"]

    assert_config_error(
        config,
        "Configuration error: missing required key 'processes'",
    )


def test_validate_config_requires_processes_list():
    config = valid_config()
    config["processes"] = {"name": "explorer.exe"}

    assert_config_error(config, "Configuration error: processes must be a list")


def test_validate_config_requires_process_item_dictionary():
    config = valid_config()
    config["processes"] = ["explorer.exe"]

    assert_config_error(
        config,
        r"Configuration error: processes\[0\] must be a dictionary",
    )


def test_validate_config_requires_process_name():
    config = valid_config()
    config["processes"] = [{}]

    assert_config_error(
        config,
        r"Configuration error: processes\[0\].name is required",
    )


def test_validate_config_requires_non_empty_process_name():
    config = valid_config()
    config["processes"] = [{"name": ""}]

    assert_config_error(
        config,
        r"Configuration error: processes\[0\].name must be a non-empty string",
    )


def test_validate_config_requires_tcp_list():
    config = valid_config()
    config["tcp"] = {"host": "localhost", "port": 80, "timeout": 2}

    assert_config_error(config, "Configuration error: tcp must be a list")


def test_validate_config_requires_tcp_item_dictionary():
    config = valid_config()
    config["tcp"] = ["localhost:80"]

    assert_config_error(
        config,
        r"Configuration error: tcp\[0\] must be a dictionary",
    )


def test_validate_config_requires_tcp_host():
    config = valid_config()
    config["tcp"] = [{"port": 80, "timeout": 2}]

    assert_config_error(
        config,
        r"Configuration error: tcp\[0\].host is required",
    )


def test_validate_config_requires_non_empty_tcp_host():
    config = valid_config()
    config["tcp"] = [{"host": "", "port": 80, "timeout": 2}]

    assert_config_error(
        config,
        r"Configuration error: tcp\[0\].host must be a non-empty string",
    )


def test_validate_config_requires_tcp_port():
    config = valid_config()
    config["tcp"] = [{"host": "localhost", "timeout": 2}]

    assert_config_error(
        config,
        r"Configuration error: tcp\[0\].port is required",
    )


def test_validate_config_requires_integer_tcp_port():
    config = valid_config()
    config["tcp"] = [{"host": "localhost", "port": "80", "timeout": 2}]

    assert_config_error(
        config,
        r"Configuration error: tcp\[0\].port must be an integer",
    )


def test_validate_config_rejects_tcp_port_below_range():
    config = valid_config()
    config["tcp"] = [{"host": "localhost", "port": 0, "timeout": 2}]

    assert_config_error(
        config,
        r"Configuration error: tcp\[0\].port must be between 1 and 65535",
    )


def test_validate_config_rejects_tcp_port_above_range():
    config = valid_config()
    config["tcp"] = [{"host": "localhost", "port": 65536, "timeout": 2}]

    assert_config_error(
        config,
        r"Configuration error: tcp\[0\].port must be between 1 and 65535",
    )


def test_validate_config_rejects_tcp_timeout_wrong_type():
    config = valid_config()
    config["tcp"] = [{"host": "localhost", "port": 80, "timeout": "2"}]

    assert_config_error(
        config,
        r"Configuration error: tcp\[0\].timeout must be a number",
    )


def test_validate_config_rejects_tcp_timeout_not_greater_than_zero():
    config = valid_config()
    config["tcp"] = [{"host": "localhost", "port": 80, "timeout": 0}]

    assert_config_error(
        config,
        r"Configuration error: tcp\[0\].timeout must be greater than 0",
    )


def test_validate_config_requires_http_list():
    config = valid_config()
    config["http"] = {"url": "https://httpbin.org/status/200", "timeout": 3}

    assert_config_error(config, "Configuration error: http must be a list")


def test_validate_config_requires_http_item_dictionary():
    config = valid_config()
    config["http"] = ["https://httpbin.org/status/200"]

    assert_config_error(
        config,
        r"Configuration error: http\[0\] must be a dictionary",
    )


def test_validate_config_requires_http_url():
    config = valid_config()
    config["http"] = [{"timeout": 3}]

    assert_config_error(
        config,
        r"Configuration error: http\[0\].url is required",
    )


def test_validate_config_rejects_http_url_wrong_scheme():
    config = valid_config()
    config["http"] = [{"url": "ftp://example.com", "timeout": 3}]

    assert_config_error(
        config,
        r"Configuration error: http\[0\].url must start with http:// or https://",
    )


def test_validate_config_rejects_http_timeout_wrong_type():
    config = valid_config()
    config["http"] = [{"url": "https://httpbin.org/status/200", "timeout": "3"}]

    assert_config_error(
        config,
        r"Configuration error: http\[0\].timeout must be a number",
    )


def test_validate_config_rejects_http_timeout_not_greater_than_zero():
    config = valid_config()
    config["http"] = [{"url": "https://httpbin.org/status/200", "timeout": 0}]

    assert_config_error(
        config,
        r"Configuration error: http\[0\].timeout must be greater than 0",
    )


def test_load_config_returns_valid_yaml_dictionary(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
processes:
  - name: explorer.exe
tcp:
  - host: localhost
    port: 80
    timeout: 2
http:
  - url: https://httpbin.org/status/200
    timeout: 3
""",
        encoding="utf-8",
    )

    result = load_config(config_file)

    assert result == valid_config()


def test_load_config_raises_file_not_found_for_missing_file(tmp_path):
    missing_file = tmp_path / "missing.yaml"

    with pytest.raises(FileNotFoundError):
        load_config(missing_file)


def test_load_config_raises_value_error_for_invalid_yaml(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("process: [invalid", encoding="utf-8")

    with pytest.raises(ValueError):
        load_config(config_file)


def test_load_config_validates_automatically(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
tcp:
  - host: localhost
    port: 80
    timeout: 2
http:
  - url: https://httpbin.org/status/200
    timeout: 3
""",
        encoding="utf-8",
    )

    with pytest.raises(
        ValueError,
        match="Configuration error: missing required key 'processes'",
    ):
        load_config(config_file)

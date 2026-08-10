import pytest

from infrapulse.config import load_config


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

    assert result == {
        "processes": [{"name": "explorer.exe"}],
        "tcp": [{"host": "localhost", "port": 80, "timeout": 2}],
        "http": [{"url": "https://httpbin.org/status/200", "timeout": 3}],
    }


def test_load_config_raises_file_not_found_for_missing_file(tmp_path):
    missing_file = tmp_path / "missing.yaml"

    with pytest.raises(FileNotFoundError):
        load_config(missing_file)


def test_load_config_raises_value_error_for_invalid_yaml(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("process: [invalid", encoding="utf-8")

    with pytest.raises(ValueError):
        load_config(config_file)

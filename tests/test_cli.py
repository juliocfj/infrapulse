from main import parse_args


def test_parse_args_uses_default_config():
    args = parse_args([])

    assert args.config == "config.yaml"


def test_parse_args_accepts_custom_config():
    args = parse_args(["--config", "custom.yaml"])

    assert args.config == "custom.yaml"

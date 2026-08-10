import json

from main import parse_args, render_json_report


def test_parse_args_uses_default_config():
    args = parse_args([])

    assert args.config == "config.yaml"
    assert args.json is False


def test_parse_args_accepts_custom_config():
    args = parse_args(["--config", "custom.yaml"])

    assert args.config == "custom.yaml"


def test_parse_args_accepts_json_output():
    args = parse_args(["--json"])

    assert args.json is True


def test_parse_args_accepts_config_and_json_output():
    args = parse_args(["--config", "custom.yaml", "--json"])

    assert args.config == "custom.yaml"
    assert args.json is True


def test_render_json_report_outputs_valid_json():
    report = {
        "overall_status": "critical",
        "checks": [
            {
                "metric": "http",
                "value": None,
                "unit": "status_code",
                "status": "critical",
                "url": "http://localhost:80",
                "reachable": False,
                "response_time_ms": None,
            }
        ],
    }

    output = render_json_report(report)

    assert json.loads(output) == report

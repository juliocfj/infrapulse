import json
from unittest.mock import call, patch

from main import collect_health_report, parse_args, render_json_report


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


def test_collect_health_report_runs_multiple_targets():
    config = {
        "processes": [
            {"name": "explorer.exe"},
            {"name": "python.exe"},
        ],
        "tcp": [
            {"host": "localhost", "port": 80, "timeout": 2},
            {"host": "localhost", "port": 443, "timeout": 2},
        ],
        "http": [
            {"url": "https://example.com/health", "timeout": 3},
            {"url": "https://example.com/status", "timeout": 3},
        ],
    }
    cpu_result = {
        "metric": "cpu",
        "value": 10,
        "unit": "%",
        "status": "healthy",
    }
    memory_result = {
        "metric": "memory",
        "value": 20,
        "unit": "%",
        "status": "healthy",
    }
    disk_result = {
        "metric": "disk",
        "value": 30,
        "unit": "%",
        "status": "healthy",
        "total_bytes": 100,
        "used_bytes": 30,
        "free_bytes": 70,
    }
    uptime_result = {
        "metric": "uptime",
        "value": 3660,
        "unit": "seconds",
        "days": 0,
        "hours": 1,
        "minutes": 1,
    }
    process_results = [
        {
            "metric": "process",
            "value": "explorer.exe",
            "unit": "state",
            "status": "healthy",
            "running": True,
        },
        {
            "metric": "process",
            "value": "python.exe",
            "unit": "state",
            "status": "critical",
            "running": False,
        },
    ]
    port_results = [
        {
            "metric": "tcp_port",
            "value": 80,
            "unit": "port",
            "status": "critical",
            "host": "localhost",
            "reachable": False,
        },
        {
            "metric": "tcp_port",
            "value": 443,
            "unit": "port",
            "status": "healthy",
            "host": "localhost",
            "reachable": True,
        },
    ]
    http_results = [
        {
            "metric": "http",
            "value": 200,
            "unit": "status_code",
            "status": "healthy",
            "url": "https://example.com/health",
            "reachable": True,
            "response_time_ms": 10,
        },
        {
            "metric": "http",
            "value": 500,
            "unit": "status_code",
            "status": "critical",
            "url": "https://example.com/status",
            "reachable": True,
            "response_time_ms": 20,
        },
    ]

    with (
        patch("main.check_cpu", return_value=cpu_result),
        patch("main.check_memory", return_value=memory_result),
        patch("main.check_disk", return_value=disk_result),
        patch("main.check_uptime", return_value=uptime_result),
        patch("main.check_process", side_effect=process_results) as check_process,
        patch("main.check_port", side_effect=port_results) as check_port,
        patch("main.check_http", side_effect=http_results) as check_http,
    ):
        report = collect_health_report(config)

    assert check_process.call_args_list == [
        call("explorer.exe"),
        call("python.exe"),
    ]
    assert check_port.call_args_list == [
        call("localhost", 80, 2),
        call("localhost", 443, 2),
    ]
    assert check_http.call_args_list == [
        call("https://example.com/health", 3),
        call("https://example.com/status", 3),
    ]
    assert report["overall_status"] == "critical"
    assert report["checks"] == [
        cpu_result,
        memory_result,
        disk_result,
        uptime_result,
        *process_results,
        *port_results,
        *http_results,
    ]
    assert json.loads(render_json_report(report)) == report

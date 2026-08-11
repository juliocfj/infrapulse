import argparse
import json
import sys

from infrapulse.checks.cpu import check_cpu
from infrapulse.checks.disk import check_disk
from infrapulse.checks.http import check_http
from infrapulse.checks.memory import check_memory
from infrapulse.checks.port import check_port
from infrapulse.checks.process import check_process
from infrapulse.checks.uptime import check_uptime
from infrapulse.config import load_config
from infrapulse.health import calculate_overall_status


def bytes_to_gb(value):
    return value / (1024**3)


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description="InfraPulse infrastructure health monitor"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to the YAML configuration file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the health report as JSON",
    )
    return parser.parse_args(args)


def collect_health_report(config):
    cpu_result = check_cpu()
    disk_result = check_disk()
    memory_result = check_memory()
    uptime_result = check_uptime()

    process_results = [
        check_process(process["name"]) for process in config["processes"]
    ]
    port_results = [
        check_port(target["host"], target["port"], target["timeout"])
        for target in config["tcp"]
    ]
    http_results = [
        check_http(target["url"], target["timeout"]) for target in config["http"]
    ]

    checks = [
        cpu_result,
        memory_result,
        disk_result,
        uptime_result,
        *process_results,
        *port_results,
        *http_results,
    ]

    overall_status = calculate_overall_status(checks)

    return {
        "overall_status": overall_status,
        "checks": checks,
    }


def render_json_report(report):
    return json.dumps(report, indent=2)


def render_json_error(message):
    return json.dumps(
        {
            "error": "configuration_error",
            "message": message,
        },
        indent=2,
    )


def print_human_report(report):
    overall_status = report["overall_status"]

    print("InfraPulse - Infrastructure Health Monitor")
    print()

    for result in report["checks"]:
        if result["metric"] == "cpu":
            print("CPU")
            print(f"Usage: {result['value']}{result['unit']}")
            print(f"Status: {result['status'].upper()}")
            print()
        elif result["metric"] == "memory":
            print("Memory")
            print(f"Usage: {result['value']}{result['unit']}")
            print(f"Status: {result['status'].upper()}")
            print()
        elif result["metric"] == "disk":
            print("Disk")
            print(f"Usage: {result['value']}{result['unit']}")
            print(f"Total: {bytes_to_gb(result['total_bytes']):.1f} GB")
            print(f"Used: {bytes_to_gb(result['used_bytes']):.1f} GB")
            print(f"Free: {bytes_to_gb(result['free_bytes']):.1f} GB")
            print(f"Status: {result['status'].upper()}")
            print()
        elif result["metric"] == "uptime":
            print("Uptime")
            print(
                f"{result['days']} days, "
                f"{result['hours']} hours, "
                f"{result['minutes']} minutes"
            )
            print()
        elif result["metric"] == "process":
            print("Process")
            print(f"Name: {result['value']}")
            print(f"Running: {'YES' if result['running'] else 'NO'}")
            print(f"Status: {result['status'].upper()}")
            print()
        elif result["metric"] == "tcp_port":
            print("TCP Port")
            print(f"Host: {result['host']}")
            print(f"Port: {result['value']}")
            print(f"Reachable: {'YES' if result['reachable'] else 'NO'}")
            print(f"Status: {result['status'].upper()}")
            print()
        elif result["metric"] == "http":
            print("HTTP Endpoint")
            print(f"URL: {result['url']}")
            print(f"Reachable: {'YES' if result['reachable'] else 'NO'}")
            print(f"Status Code: {result['value']}")
            print(f"Response Time: {result['response_time_ms']} ms")
            print(f"Status: {result['status'].upper()}")
            print()

    print("Overall Health")
    print(f"Status: {overall_status.upper()}")


def main(args=None):
    parsed_args = parse_args(args)

    try:
        config = load_config(parsed_args.config)
    except (FileNotFoundError, ValueError) as error:
        if parsed_args.json:
            print(render_json_error(str(error)))
        else:
            print(error)
        return 3

    report = collect_health_report(config)

    if parsed_args.json:
        print(render_json_report(report))
    else:
        print_human_report(report)

    exit_codes = {
        "healthy": 0,
        "warning": 1,
        "critical": 2,
    }

    return exit_codes[report["overall_status"]]


if __name__ == "__main__":
    sys.exit(main())

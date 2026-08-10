import argparse
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
    return parser.parse_args(args)


def main(args=None):
    parsed_args = parse_args(args)
    config = load_config(parsed_args.config)

    print("InfraPulse - Infrastructure Health Monitor")
    print()

    cpu_result = check_cpu()
    disk_result = check_disk()
    http_result = check_http(config["http"]["url"], config["http"]["timeout"])
    memory_result = check_memory()
    port_result = check_port(
        config["tcp"]["host"],
        config["tcp"]["port"],
        config["tcp"]["timeout"],
    )
    process_result = check_process(config["process"]["name"])
    uptime_result = check_uptime()

    overall_status = calculate_overall_status(
        [
            cpu_result,
            memory_result,
            disk_result,
            process_result,
            port_result,
            http_result,
        ]
    )

    print("CPU")
    print(f"Usage: {cpu_result['value']}{cpu_result['unit']}")
    print(f"Status: {cpu_result['status'].upper()}")
    print()

    print("Memory")
    print(f"Usage: {memory_result['value']}{memory_result['unit']}")
    print(f"Status: {memory_result['status'].upper()}")
    print()

    print("Disk")
    print(f"Usage: {disk_result['value']}{disk_result['unit']}")
    print(f"Total: {bytes_to_gb(disk_result['total_bytes']):.1f} GB")
    print(f"Used: {bytes_to_gb(disk_result['used_bytes']):.1f} GB")
    print(f"Free: {bytes_to_gb(disk_result['free_bytes']):.1f} GB")
    print(f"Status: {disk_result['status'].upper()}")
    print()

    print("Uptime")
    print(
        f"{uptime_result['days']} days, "
        f"{uptime_result['hours']} hours, "
        f"{uptime_result['minutes']} minutes"
    )
    print()

    print("Process")
    print(f"Name: {process_result['value']}")
    print(f"Running: {'YES' if process_result['running'] else 'NO'}")
    print(f"Status: {process_result['status'].upper()}")
    print()

    print("TCP Port")
    print(f"Host: {port_result['host']}")
    print(f"Port: {port_result['value']}")
    print(f"Reachable: {'YES' if port_result['reachable'] else 'NO'}")
    print(f"Status: {port_result['status'].upper()}")
    print()

    print("HTTP Endpoint")
    print(f"URL: {http_result['url']}")
    print(f"Reachable: {'YES' if http_result['reachable'] else 'NO'}")
    print(f"Status Code: {http_result['value']}")
    print(f"Response Time: {http_result['response_time_ms']} ms")
    print(f"Status: {http_result['status'].upper()}")
    print()

    print("Overall Health")
    print(f"Status: {overall_status.upper()}")

    exit_codes = {
        "healthy": 0,
        "warning": 1,
        "critical": 2,
    }

    return exit_codes[overall_status]


if __name__ == "__main__":
    sys.exit(main())

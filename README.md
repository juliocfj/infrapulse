# InfraPulse

[![CI](https://github.com/juliocfj/infrapulse/actions/workflows/ci.yml/badge.svg)](https://github.com/juliocfj/infrapulse/actions/workflows/ci.yml)

InfraPulse v1.0.0

InfraPulse is a lightweight infrastructure health monitoring and troubleshooting tool built with Python. It provides simple command-line checks for common system and service health signals.

v1.0.0 is the first stable portfolio release of InfraPulse.

Repository: [juliocfj/infrapulse](https://github.com/juliocfj/infrapulse)

## Quick Start

```bash
git clone https://github.com/juliocfj/infrapulse.git
cd infrapulse
python -m venv .venv
python -m pip install -r requirements.txt
python main.py
```

## Features

- CPU utilization monitoring
- Memory utilization monitoring
- Disk usage monitoring
- System uptime
- Process monitoring
- TCP port reachability
- HTTP endpoint monitoring
- Multiple process, TCP, and HTTP targets
- Overall health status
- Health-based exit codes
- YAML configuration
- Configuration validation
- JSON output
- Docker support
- Automated unit tests
- Ruff linting
- GitHub Actions CI

## Health Status

InfraPulse uses three health states:

- `HEALTHY`: the check is within the expected range or reachable.
- `WARNING`: the check is degraded but not critical.
- `CRITICAL`: the check failed or crossed a critical threshold.

The most severe status determines the Overall Health. For example, if one check is `CRITICAL`, the Overall Health is `CRITICAL`.

## Exit Codes

InfraPulse exits with a code based on the Overall Health:

- `0` = healthy
- `1` = warning
- `2` = critical
- `3` = configuration error

Exit codes make the tool useful for scripts, CI/CD pipelines, scheduled tasks, and automation systems that need to detect health without parsing the full CLI output.

## Requirements

- Python 3.12+

## Installation

```bash
git clone https://github.com/juliocfj/infrapulse.git
cd infrapulse
```

Create and activate a Windows virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Configuration

InfraPulse reads monitoring targets from `config.yaml`. Configuration is validated before health checks run. Users can monitor more than one process, TCP endpoint, and HTTP endpoint by adding more items to each list.

```yaml
processes:
  - name: explorer.exe

tcp:
  - host: localhost
    port: 80
    timeout: 2

http:
  - url: https://httpbin.org/status/200
    timeout: 3
```

These values can be changed without modifying Python code. `explorer.exe` is only an example for Windows; Linux users should configure an appropriate process such as `nginx`.

Invalid configuration returns a clear error and exits with code `3`:

```text
Configuration error: tcp[0].port must be an integer
```

## Usage

```bash
python main.py
```

Check the installed project version:

```bash
python main.py --version
```

Example output:

```text
InfraPulse - Infrastructure Health Monitor

CPU
Usage: 20.5%
Status: HEALTHY

Memory
Usage: 72.1%
Status: HEALTHY

TCP Port
Host: localhost
Port: 80
Reachable: NO
Status: CRITICAL

Overall Health
Status: CRITICAL
```

## JSON Output

InfraPulse can also return machine-readable JSON output:

```bash
python main.py --json
```

Use JSON output with a specific configuration file:

```bash
python main.py --config config.yaml --json
```

JSON mode is useful for scripts, automation, CI/CD pipelines, and integrations.

Example JSON output:

```json
{
  "overall_status": "critical",
  "checks": [
    {
      "metric": "tcp_port",
      "value": 80,
      "unit": "port",
      "status": "critical",
      "host": "localhost",
      "reachable": false
    }
  ]
}
```

Exit codes remain the same in JSON mode:

- `0` = healthy
- `1` = warning
- `2` = critical
- `3` = configuration error

## Docker

InfraPulse can run natively on Windows and Linux:

```bash
python main.py
```

Native execution uses `config.yaml` by default and is recommended when InfraPulse should monitor the actual Windows or Linux host.

You can also run InfraPulse with a custom native configuration file:

```bash
python main.py --config another-config.yaml
```

The Docker image uses a Linux-based Python 3.12 container. The same Linux container image can be run from Docker on Windows or Linux.

When running in Docker, system and process checks observe the container environment by default. Docker execution does not automatically monitor the Windows or Linux host. A Windows-specific process such as `explorer.exe` will not exist inside the Linux container.

The Docker image uses `config.docker.yaml` by default. This file is intentionally container-oriented and can be adjusted for Linux/container-appropriate targets. HTTP, TCP, and process targets may report `CRITICAL` if the configured target is unavailable from inside the container.

Build the Docker image:

```bash
docker build -t infrapulse .
```

Run the container:

```bash
docker run --rm infrapulse
```

InfraPulse exit codes are preserved when the container exits:

- `0` = healthy
- `1` = warning
- `2` = critical
- `3` = configuration error

This means `docker run` may exit with code `1` or `2` even when Docker itself worked correctly.

## Tests

Run the test suite with:

```bash
python -m pytest -v
```

The test suite covers health checks, configuration validation, CLI behavior, JSON output, and Overall Health status calculation.

## Continuous Integration

GitHub Actions automatically:

1. checks out the repository
2. sets up Python 3.12
3. installs dependencies
4. runs Ruff
5. runs pytest with coverage
6. validates the Docker image build

CI runs on `push` and `pull_request`.

## Project Structure

```text
.github/
  workflows/
    ci.yml
CHANGELOG.md
Dockerfile
RELEASE_CHECKLIST.md
config.docker.yaml
config.yaml
main.py
requirements.txt
infrapulse/
  config.py
  health.py
  version.py
  checks/
tests/
  test_health.py
```

## Technologies

- Python
- psutil
- Requests
- PyYAML
- pytest
- GitHub Actions

## Project Purpose

InfraPulse was created as a practical infrastructure/support engineering portfolio project focused on monitoring, troubleshooting, automation, and CI concepts.

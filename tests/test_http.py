from unittest.mock import MagicMock, patch

import requests

from infrapulse.checks.http import check_http


def make_response(status_code, response_time_seconds=0.245):
    response = MagicMock()
    response.status_code = status_code
    response.elapsed.total_seconds.return_value = response_time_seconds
    return response


def test_http_200_response_returns_healthy():
    with patch("infrapulse.checks.http.requests.get") as get:
        get.return_value = make_response(200)

        result = check_http("https://example.com")

    assert result["value"] == 200
    assert result["reachable"] is True
    assert result["response_time_ms"] == 245
    assert result["status"] == "healthy"


def test_http_302_response_returns_warning():
    with patch("infrapulse.checks.http.requests.get") as get:
        get.return_value = make_response(302)

        result = check_http("https://example.com")

    assert result["value"] == 302
    assert result["reachable"] is True
    assert result["response_time_ms"] == 245
    assert result["status"] == "warning"


def test_http_500_response_returns_critical():
    with patch("infrapulse.checks.http.requests.get") as get:
        get.return_value = make_response(500)

        result = check_http("https://example.com")

    assert result["value"] == 500
    assert result["reachable"] is True
    assert result["response_time_ms"] == 245
    assert result["status"] == "critical"


def test_request_exception_returns_critical():
    with patch("infrapulse.checks.http.requests.get") as get:
        get.side_effect = requests.RequestException

        result = check_http("https://example.com")

    assert result["value"] is None
    assert result["reachable"] is False
    assert result["response_time_ms"] is None
    assert result["status"] == "critical"

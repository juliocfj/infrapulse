from unittest.mock import MagicMock, patch

from infrapulse.checks.port import check_port


def test_successful_tcp_connection_returns_healthy():
    connection = MagicMock()

    with patch("infrapulse.checks.port.socket.create_connection") as create_connection:
        create_connection.return_value.__enter__.return_value = connection

        result = check_port("localhost", 80)

    assert result["reachable"] is True
    assert result["status"] == "healthy"


def test_failed_tcp_connection_returns_critical():
    with patch("infrapulse.checks.port.socket.create_connection") as create_connection:
        create_connection.side_effect = OSError

        result = check_port("localhost", 80)

    assert result["reachable"] is False
    assert result["status"] == "critical"

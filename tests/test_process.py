from unittest.mock import MagicMock, patch

import psutil

from infrapulse.checks.process import check_process


class AccessDeniedProcess:
    @property
    def info(self):
        raise psutil.AccessDenied(pid=1)


class NoSuchProcess:
    @property
    def info(self):
        raise psutil.NoSuchProcess(pid=2)


def test_matching_process_exists_case_insensitive():
    process = MagicMock()
    process.info = {"name": "EXPLORER.EXE"}

    with patch("infrapulse.checks.process.psutil.process_iter") as process_iter:
        process_iter.return_value = [process]

        result = check_process("explorer.exe")

    assert result["running"] is True
    assert result["status"] == "healthy"


def test_process_does_not_exist_returns_critical():
    process = MagicMock()
    process.info = {"name": "python.exe"}

    with patch("infrapulse.checks.process.psutil.process_iter") as process_iter:
        process_iter.return_value = [process]

        result = check_process("explorer.exe")

    assert result["running"] is False
    assert result["status"] == "critical"


def test_process_inspection_errors_are_ignored():
    matching_process = MagicMock()
    matching_process.info = {"name": "explorer.exe"}

    with patch("infrapulse.checks.process.psutil.process_iter") as process_iter:
        process_iter.return_value = [
            AccessDeniedProcess(),
            NoSuchProcess(),
            matching_process,
        ]

        result = check_process("explorer.exe")

    assert result["running"] is True
    assert result["status"] == "healthy"

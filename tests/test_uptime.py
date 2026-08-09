from datetime import datetime, timezone
from unittest.mock import patch

from infrapulse.checks.uptime import check_uptime


def test_uptime_uses_controlled_timestamps():
    boot_time = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    current_time = datetime(2026, 1, 2, 2, 3, 30, tzinfo=timezone.utc)

    with (
        patch("infrapulse.checks.uptime.psutil.boot_time") as boot_time_mock,
        patch("infrapulse.checks.uptime.datetime") as datetime_mock,
    ):
        boot_time_mock.return_value = boot_time.timestamp()
        datetime_mock.fromtimestamp.return_value = boot_time
        datetime_mock.now.return_value = current_time

        result = check_uptime()

    assert result["metric"] == "uptime"
    assert result["value"] == 93810
    assert result["unit"] == "seconds"
    assert result["days"] == 1
    assert result["hours"] == 2
    assert result["minutes"] == 3

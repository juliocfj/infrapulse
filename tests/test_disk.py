from types import SimpleNamespace
from unittest.mock import patch

import pytest

from infrapulse.checks.disk import check_disk


@pytest.mark.parametrize(
    ("usage_percent", "expected_status"),
    [
        (50, "healthy"),
        (80, "warning"),
        (89, "warning"),
        (90, "critical"),
    ],
)
def test_disk_thresholds_and_byte_values(usage_percent, expected_status):
    disk_usage = SimpleNamespace(
        percent=usage_percent,
        total=1000,
        used=600,
        free=400,
    )

    with patch("infrapulse.checks.disk.psutil.disk_usage") as disk_usage_mock:
        disk_usage_mock.return_value = disk_usage

        result = check_disk()

    assert result["metric"] == "disk"
    assert result["value"] == usage_percent
    assert result["unit"] == "%"
    assert result["status"] == expected_status
    assert result["total_bytes"] == 1000
    assert result["used_bytes"] == 600
    assert result["free_bytes"] == 400

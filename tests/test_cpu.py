from unittest.mock import patch

import pytest

from infrapulse.checks.cpu import check_cpu


@pytest.mark.parametrize(
    ("usage_percent", "expected_status"),
    [
        (50, "healthy"),
        (70, "warning"),
        (89, "warning"),
        (90, "critical"),
    ],
)
def test_cpu_thresholds(usage_percent, expected_status):
    with patch("infrapulse.checks.cpu.psutil.cpu_percent") as cpu_percent:
        cpu_percent.return_value = usage_percent

        result = check_cpu()

    assert result["metric"] == "cpu"
    assert result["value"] == usage_percent
    assert result["unit"] == "%"
    assert result["status"] == expected_status

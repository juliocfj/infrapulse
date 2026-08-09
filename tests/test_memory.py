from types import SimpleNamespace
from unittest.mock import patch

import pytest

from infrapulse.checks.memory import check_memory


@pytest.mark.parametrize(
    ("usage_percent", "expected_status"),
    [
        (50, "healthy"),
        (75, "warning"),
        (89, "warning"),
        (90, "critical"),
    ],
)
def test_memory_thresholds(usage_percent, expected_status):
    memory_usage = SimpleNamespace(percent=usage_percent)

    with patch("infrapulse.checks.memory.psutil.virtual_memory") as virtual_memory:
        virtual_memory.return_value = memory_usage

        result = check_memory()

    assert result["metric"] == "memory"
    assert result["value"] == usage_percent
    assert result["unit"] == "%"
    assert result["status"] == expected_status

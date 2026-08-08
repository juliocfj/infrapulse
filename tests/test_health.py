from infrapulse.health import calculate_overall_status


def test_all_checks_healthy():
    results = [
        {"metric": "cpu", "status": "healthy"},
        {"metric": "memory", "status": "healthy"},
        {"metric": "disk", "status": "healthy"},
    ]

    assert calculate_overall_status(results) == "healthy"


def test_warning_without_critical_returns_warning():
    results = [
        {"metric": "cpu", "status": "healthy"},
        {"metric": "memory", "status": "warning"},
        {"metric": "disk", "status": "healthy"},
    ]

    assert calculate_overall_status(results) == "warning"


def test_critical_returns_critical():
    results = [
        {"metric": "cpu", "status": "healthy"},
        {"metric": "memory", "status": "critical"},
        {"metric": "disk", "status": "healthy"},
    ]

    assert calculate_overall_status(results) == "critical"


def test_warning_and_critical_returns_critical():
    results = [
        {"metric": "cpu", "status": "warning"},
        {"metric": "memory", "status": "critical"},
        {"metric": "disk", "status": "healthy"},
    ]

    assert calculate_overall_status(results) == "critical"


def test_result_without_status_is_ignored():
    results = [
        {"metric": "cpu", "status": "healthy"},
        {"metric": "uptime", "value": 3600, "unit": "seconds"},
        {"metric": "disk", "status": "healthy"},
    ]

    assert calculate_overall_status(results) == "healthy"

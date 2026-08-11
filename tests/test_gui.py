import importlib
from unittest.mock import patch

import gui.app as gui_app


def test_importing_gui_app_does_not_launch_application():
    app = importlib.import_module("gui.app")

    assert hasattr(app, "InfraPulseGUI")
    assert hasattr(app, "main")


class FakeVar:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class FakeLabel:
    def __init__(self):
        self.options = {}

    def configure(self, **kwargs):
        self.options.update(kwargs)


def make_gui():
    gui = gui_app.InfraPulseGUI.__new__(gui_app.InfraPulseGUI)
    gui.status_message = FakeVar()
    gui.overall_status = FakeVar("NOT CHECKED")
    gui.overall_description = FakeVar(
        "Run one or more checks to calculate overall health."
    )
    gui.overall_status_label = FakeLabel()
    gui.latest_results = {}
    gui.metric_cards = {
        "cpu": make_card(),
        "memory": make_card(),
        "disk": make_card(),
        "uptime": make_card(),
    }
    gui.service_inputs = {
        "process_name": FakeVar("explorer.exe"),
        "tcp_host": FakeVar("github.com"),
        "tcp_port": FakeVar("443"),
        "tcp_timeout": FakeVar("3"),
        "http_url": FakeVar("https://github.com"),
        "http_timeout": FakeVar("5"),
    }
    gui.service_cards = {
        "process": make_service_card(),
        "tcp": make_service_card(),
        "http": make_service_card(include_extra=True),
    }
    return gui


def make_card():
    return {
        "value": FakeVar("--"),
        "status": FakeVar("NOT CHECKED"),
        "status_label": FakeLabel(),
    }


def make_service_card(include_extra=False):
    card = {
        "target": FakeVar("Target: --"),
        "detail": FakeVar("Detail: --"),
        "status": FakeVar("Status: NOT CHECKED"),
        "status_label": FakeLabel(),
    }
    if include_extra:
        card["extra"] = FakeVar("Extra: --")

    return card


def test_cpu_check_updates_cpu_value_and_status():
    gui = make_gui()

    with patch(
        "gui.app.check_cpu",
        return_value={"metric": "cpu", "value": 15.4, "unit": "%", "status": "healthy"},
    ):
        gui._run_cpu_check()

    assert gui.metric_cards["cpu"]["value"].get() == "15.4%"
    assert gui.metric_cards["cpu"]["status"].get() == "HEALTHY"
    assert (
        gui.metric_cards["cpu"]["status_label"].options["style"]
        == "HealthyStatus.TLabel"
    )


def test_memory_check_updates_memory_value_and_preserves_warning_status():
    gui = make_gui()

    with patch(
        "gui.app.check_memory",
        return_value={
            "metric": "memory",
            "value": 75.0,
            "unit": "%",
            "status": "warning",
        },
    ):
        gui._run_memory_check()

    assert gui.metric_cards["memory"]["value"].get() == "75.0%"
    assert gui.metric_cards["memory"]["status"].get() == "WARNING"
    assert (
        gui.metric_cards["memory"]["status_label"].options["style"]
        == "WarningStatus.TLabel"
    )


def test_disk_check_updates_disk_value_and_preserves_critical_status():
    gui = make_gui()

    with patch(
        "gui.app.check_disk",
        return_value={
            "metric": "disk",
            "value": 92.1,
            "unit": "%",
            "status": "critical",
            "total_bytes": 100,
            "used_bytes": 92,
            "free_bytes": 8,
        },
    ):
        gui._run_disk_check()

    assert gui.metric_cards["disk"]["value"].get() == "92.1%"
    assert gui.metric_cards["disk"]["status"].get() == "CRITICAL"
    assert (
        gui.metric_cards["disk"]["status_label"].options["style"]
        == "CriticalStatus.TLabel"
    )


def test_uptime_check_formats_uptime_as_info():
    gui = make_gui()

    with patch(
        "gui.app.check_uptime",
        return_value={
            "metric": "uptime",
            "value": 189060,
            "unit": "seconds",
            "days": 2,
            "hours": 4,
            "minutes": 31,
        },
    ):
        gui._run_uptime_check()

    assert gui.metric_cards["uptime"]["value"].get() == "2d 4h 31m"
    assert gui.metric_cards["uptime"]["status"].get() == "INFO"
    assert (
        gui.metric_cards["uptime"]["status_label"].options["style"]
        == "InfoStatus.TLabel"
    )


def test_run_all_executes_all_four_system_checks():
    gui = make_gui()

    with (
        patch(
            "gui.app.check_cpu",
            return_value={
                "metric": "cpu",
                "value": 10,
                "unit": "%",
                "status": "healthy",
            },
        ) as check_cpu,
        patch(
            "gui.app.check_memory",
            return_value={
                "metric": "memory",
                "value": 20,
                "unit": "%",
                "status": "healthy",
            },
        ) as check_memory,
        patch(
            "gui.app.check_disk",
            return_value={
                "metric": "disk",
                "value": 30,
                "unit": "%",
                "status": "healthy",
                "total_bytes": 100,
                "used_bytes": 30,
                "free_bytes": 70,
            },
        ) as check_disk,
        patch(
            "gui.app.check_uptime",
            return_value={
                "metric": "uptime",
                "value": 60,
                "unit": "seconds",
                "days": 0,
                "hours": 0,
                "minutes": 1,
            },
        ) as check_uptime,
    ):
        gui._run_system_checks()

    check_cpu.assert_called_once_with()
    check_memory.assert_called_once_with()
    check_disk.assert_called_once_with()
    check_uptime.assert_called_once_with()
    assert gui.status_message.get() == "System health checks completed."


def test_check_exception_updates_card_without_propagating():
    gui = make_gui()

    with patch("gui.app.check_cpu", side_effect=RuntimeError("sensor unavailable")):
        gui._run_cpu_check()

    assert gui.metric_cards["cpu"]["value"].get() == "ERROR"
    assert gui.metric_cards["cpu"]["status"].get() == "ERROR"
    assert gui.status_message.get() == "CPU check failed: sensor unavailable"


def test_valid_process_input_calls_check_process_and_updates_card():
    gui = make_gui()
    gui.service_inputs["process_name"].set("python.exe")

    with patch(
        "gui.app.check_process",
        return_value={
            "metric": "process",
            "value": "python.exe",
            "unit": "state",
            "status": "healthy",
            "running": True,
        },
    ) as check_process:
        gui._run_process_check()

    check_process.assert_called_once_with("python.exe")
    assert gui.service_cards["process"]["target"].get() == "Target: python.exe"
    assert gui.service_cards["process"]["detail"].get() == "Running: YES"
    assert gui.service_cards["process"]["status"].get() == "Status: HEALTHY"


def test_empty_process_name_is_rejected_without_calling_check_process():
    gui = make_gui()
    gui.service_inputs["process_name"].set(" ")

    with patch("gui.app.check_process") as check_process:
        result = gui._run_process_check()

    check_process.assert_not_called()
    assert result is False
    assert gui.service_cards["process"]["status"].get() == "Status: ERROR"
    assert gui.status_message.get() == "Invalid process name: enter a process name."


def test_valid_tcp_input_calls_check_port_and_updates_card():
    gui = make_gui()

    with patch(
        "gui.app.check_port",
        return_value={
            "metric": "tcp_port",
            "value": 443,
            "unit": "port",
            "status": "healthy",
            "host": "github.com",
            "reachable": True,
        },
    ) as check_port:
        gui._run_tcp_check()

    check_port.assert_called_once_with("github.com", 443, 3.0)
    assert gui.service_cards["tcp"]["target"].get() == "Target: github.com:443"
    assert gui.service_cards["tcp"]["detail"].get() == "Reachable: YES"
    assert gui.service_cards["tcp"]["status"].get() == "Status: HEALTHY"


def test_invalid_tcp_port_is_rejected():
    gui = make_gui()
    gui.service_inputs["tcp_port"].set("99999")

    with patch("gui.app.check_port") as check_port:
        result = gui._run_tcp_check()

    check_port.assert_not_called()
    assert result is False
    assert gui.service_cards["tcp"]["status"].get() == "Status: ERROR"
    assert (
        gui.status_message.get()
        == "Invalid TCP port: enter a value between 1 and 65535."
    )


def test_invalid_tcp_timeout_is_rejected():
    gui = make_gui()
    gui.service_inputs["tcp_timeout"].set("0")

    with patch("gui.app.check_port") as check_port:
        result = gui._run_tcp_check()

    check_port.assert_not_called()
    assert result is False
    assert gui.service_cards["tcp"]["status"].get() == "Status: ERROR"
    assert gui.status_message.get() == "Invalid TCP timeout: enter a number greater than 0."


def test_valid_http_input_calls_check_http_and_updates_card():
    gui = make_gui()

    with patch(
        "gui.app.check_http",
        return_value={
            "metric": "http",
            "value": 200,
            "unit": "status_code",
            "status": "warning",
            "url": "https://github.com",
            "reachable": True,
            "response_time_ms": 120,
        },
    ) as check_http:
        gui._run_http_check()

    check_http.assert_called_once_with("https://github.com", 5.0)
    assert gui.service_cards["http"]["target"].get() == "Target: https://github.com"
    assert gui.service_cards["http"]["detail"].get() == "Status Code: 200"
    assert gui.service_cards["http"]["extra"].get() == "Response Time: 120 ms"
    assert gui.service_cards["http"]["status"].get() == "Status: WARNING"


def test_invalid_http_url_scheme_is_rejected():
    gui = make_gui()
    gui.service_inputs["http_url"].set("ftp://github.com")

    with patch("gui.app.check_http") as check_http:
        result = gui._run_http_check()

    check_http.assert_not_called()
    assert result is False
    assert gui.service_cards["http"]["status"].get() == "Status: ERROR"
    assert (
        gui.status_message.get()
        == "Invalid HTTP URL: enter a URL starting with http:// or https://."
    )


def test_invalid_http_timeout_is_rejected():
    gui = make_gui()
    gui.service_inputs["http_timeout"].set("zero")

    with patch("gui.app.check_http") as check_http:
        result = gui._run_http_check()

    check_http.assert_not_called()
    assert result is False
    assert gui.service_cards["http"]["status"].get() == "Status: ERROR"
    assert gui.status_message.get() == "Invalid HTTP timeout: enter a number greater than 0."


def test_service_check_exception_becomes_error_without_propagating():
    gui = make_gui()

    with patch("gui.app.check_http", side_effect=RuntimeError("network unavailable")):
        result = gui._run_http_check()

    assert result is False
    assert gui.service_cards["http"]["status"].get() == "Status: ERROR"
    assert gui.status_message.get() == "HTTP check failed: network unavailable"


def test_run_all_executes_system_and_service_checks_and_keeps_overall_unchecked():
    gui = make_gui()

    with (
        patch.object(gui, "_run_cpu_check", return_value=True) as cpu,
        patch.object(gui, "_run_memory_check", return_value=True) as memory,
        patch.object(gui, "_run_disk_check", return_value=True) as disk,
        patch.object(gui, "_run_uptime_check", return_value=True) as uptime,
        patch.object(gui, "_run_process_check", return_value=True) as process,
        patch.object(gui, "_run_tcp_check", return_value=True) as tcp,
        patch.object(gui, "_run_http_check", return_value=True) as http,
    ):
        gui._run_all_checks()

    cpu.assert_called_once_with()
    memory.assert_called_once_with()
    disk.assert_called_once_with()
    uptime.assert_called_once_with()
    process.assert_called_once_with()
    tcp.assert_called_once_with()
    http.assert_called_once_with()
    assert gui.status_message.get() == "All checks completed."
    assert gui.overall_status.get() == "NOT CHECKED"


def test_status_style_helper_selects_expected_styles():
    gui = make_gui()

    assert gui._get_status_style("healthy") == "HealthyStatus.TLabel"
    assert gui._get_status_style("warning") == "WarningStatus.TLabel"
    assert gui._get_status_style("critical") == "CriticalStatus.TLabel"
    assert gui._get_status_style("info") == "InfoStatus.TLabel"
    assert gui._get_status_style("not checked") == "NeutralStatus.TLabel"


def test_overall_starts_as_not_checked():
    gui = make_gui()

    gui._update_overall_health()

    assert gui.overall_status.get() == "NOT CHECKED"
    assert (
        gui.overall_description.get()
        == "Run one or more checks to calculate overall health."
    )


def test_successful_healthy_cpu_makes_overall_healthy():
    gui = make_gui()

    with patch(
        "gui.app.check_cpu",
        return_value={"metric": "cpu", "value": 10, "unit": "%", "status": "healthy"},
    ):
        gui._run_cpu_check()

    assert gui.latest_results["cpu"]["status"] == "healthy"
    assert gui.overall_status.get() == "HEALTHY"
    assert gui.overall_description.get() == "All completed checks are healthy."


def test_warning_memory_makes_overall_warning_after_healthy_cpu():
    gui = make_gui()

    gui._store_latest_result(
        "cpu",
        {"metric": "cpu", "value": 10, "unit": "%", "status": "healthy"},
    )
    with patch(
        "gui.app.check_memory",
        return_value={
            "metric": "memory",
            "value": 75,
            "unit": "%",
            "status": "warning",
        },
    ):
        gui._run_memory_check()

    assert gui.overall_status.get() == "WARNING"
    assert (
        gui.overall_description.get()
        == "One or more completed checks require attention."
    )


def test_critical_disk_dominates_warning():
    gui = make_gui()

    gui._store_latest_result(
        "memory",
        {"metric": "memory", "value": 75, "unit": "%", "status": "warning"},
    )
    with patch(
        "gui.app.check_disk",
        return_value={
            "metric": "disk",
            "value": 90,
            "unit": "%",
            "status": "critical",
            "total_bytes": 100,
            "used_bytes": 90,
            "free_bytes": 10,
        },
    ):
        gui._run_disk_check()

    assert gui.overall_status.get() == "CRITICAL"
    assert gui.overall_description.get() == "One or more completed checks are critical."


def test_process_tcp_and_http_results_contribute_to_overall():
    gui = make_gui()

    gui._store_latest_result(
        "process",
        {
            "metric": "process",
            "value": "explorer.exe",
            "unit": "state",
            "status": "healthy",
            "running": True,
        },
    )
    gui._store_latest_result(
        "tcp_port",
        {
            "metric": "tcp_port",
            "value": 443,
            "unit": "port",
            "status": "warning",
            "host": "github.com",
            "reachable": True,
        },
    )
    gui._store_latest_result(
        "http",
        {
            "metric": "http",
            "value": 500,
            "unit": "status_code",
            "status": "critical",
            "url": "https://github.com",
            "reachable": True,
            "response_time_ms": 50,
        },
    )

    assert gui.overall_status.get() == "CRITICAL"


def test_uptime_does_not_affect_overall():
    gui = make_gui()

    with patch(
        "gui.app.check_uptime",
        return_value={
            "metric": "uptime",
            "value": 60,
            "unit": "seconds",
            "days": 0,
            "hours": 0,
            "minutes": 1,
        },
    ):
        gui._run_uptime_check()

    assert "uptime" in gui.latest_results
    assert gui.overall_status.get() == "NOT CHECKED"


def test_failed_check_removes_stale_previous_result():
    gui = make_gui()
    gui._store_latest_result(
        "cpu",
        {"metric": "cpu", "value": 10, "unit": "%", "status": "healthy"},
    )

    with patch("gui.app.check_cpu", side_effect=RuntimeError("sensor unavailable")):
        gui._run_cpu_check()

    assert "cpu" not in gui.latest_results
    assert gui.overall_status.get() == "NOT CHECKED"


def test_invalid_service_inputs_remove_stale_results():
    gui = make_gui()
    gui._store_latest_result(
        "process",
        {
            "metric": "process",
            "value": "explorer.exe",
            "unit": "state",
            "status": "healthy",
            "running": True,
        },
    )
    gui._store_latest_result(
        "tcp_port",
        {
            "metric": "tcp_port",
            "value": 443,
            "unit": "port",
            "status": "healthy",
            "host": "github.com",
            "reachable": True,
        },
    )
    gui._store_latest_result(
        "http",
        {
            "metric": "http",
            "value": 200,
            "unit": "status_code",
            "status": "healthy",
            "url": "https://github.com",
            "reachable": True,
            "response_time_ms": 50,
        },
    )

    gui.service_inputs["process_name"].set("")
    gui.service_inputs["tcp_port"].set("99999")
    gui.service_inputs["http_url"].set("ftp://github.com")

    gui._run_process_check()
    gui._run_tcp_check()
    gui._run_http_check()

    assert "process" not in gui.latest_results
    assert "tcp_port" not in gui.latest_results
    assert "http" not in gui.latest_results
    assert gui.overall_status.get() == "NOT CHECKED"


def test_run_all_finishes_with_expected_overall_status():
    gui = make_gui()

    with (
        patch(
            "gui.app.check_cpu",
            return_value={
                "metric": "cpu",
                "value": 10,
                "unit": "%",
                "status": "healthy",
            },
        ),
        patch(
            "gui.app.check_memory",
            return_value={
                "metric": "memory",
                "value": 20,
                "unit": "%",
                "status": "healthy",
            },
        ),
        patch(
            "gui.app.check_disk",
            return_value={
                "metric": "disk",
                "value": 30,
                "unit": "%",
                "status": "healthy",
                "total_bytes": 100,
                "used_bytes": 30,
                "free_bytes": 70,
            },
        ),
        patch(
            "gui.app.check_uptime",
            return_value={
                "metric": "uptime",
                "value": 60,
                "unit": "seconds",
                "days": 0,
                "hours": 0,
                "minutes": 1,
            },
        ),
        patch(
            "gui.app.check_process",
            return_value={
                "metric": "process",
                "value": "explorer.exe",
                "unit": "state",
                "status": "healthy",
                "running": True,
            },
        ),
        patch(
            "gui.app.check_port",
            return_value={
                "metric": "tcp_port",
                "value": 443,
                "unit": "port",
                "status": "healthy",
                "host": "github.com",
                "reachable": True,
            },
        ),
        patch(
            "gui.app.check_http",
            return_value={
                "metric": "http",
                "value": 500,
                "unit": "status_code",
                "status": "critical",
                "url": "https://github.com",
                "reachable": True,
                "response_time_ms": 50,
            },
        ),
    ):
        gui._run_all_checks()

    assert gui.overall_status.get() == "CRITICAL"
    assert gui.status_message.get() == "All checks completed."


def test_gui_reuses_calculate_overall_status():
    gui = make_gui()
    gui.latest_results["cpu"] = {
        "metric": "cpu",
        "value": 10,
        "unit": "%",
        "status": "healthy",
    }

    with patch("gui.app.calculate_overall_status", return_value="warning") as engine:
        gui._update_overall_health()

    engine.assert_called_once_with([gui.latest_results["cpu"]])
    assert gui.overall_status.get() == "WARNING"

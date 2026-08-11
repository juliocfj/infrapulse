import tkinter as tk
from tkinter import ttk

from infrapulse.checks.cpu import check_cpu
from infrapulse.checks.disk import check_disk
from infrapulse.checks.http import check_http
from infrapulse.checks.memory import check_memory
from infrapulse.checks.port import check_port
from infrapulse.checks.process import check_process
from infrapulse.checks.uptime import check_uptime
from infrapulse.health import calculate_overall_status


class InfraPulseGUI:
    def __init__(self, root):
        self.root = root
        self.metric_cards = {}
        self.service_cards = {}
        self.service_inputs = {}
        self.latest_results = {}
        self.status_message = tk.StringVar(
            value="Check execution will be added in the next phase."
        )
        self.overall_status = tk.StringVar(value="NOT CHECKED")
        self.overall_description = tk.StringVar(
            value="Run one or more checks to calculate overall health."
        )

        self._configure_window()
        self._configure_styles()
        self._build_layout()

    def _configure_window(self):
        self.root.title("InfraPulse")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)

    def _configure_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure("App.TFrame", background="#f5f7fa")
        style.configure("Header.TFrame", background="#1f2937")
        style.configure(
            "HeaderTitle.TLabel",
            background="#1f2937",
            foreground="#f9fafb",
            font=("Segoe UI", 24, "bold"),
        )
        style.configure(
            "HeaderSubtitle.TLabel",
            background="#1f2937",
            foreground="#d1d5db",
            font=("Segoe UI", 11),
        )
        style.configure(
            "Preview.TLabel",
            background="#374151",
            foreground="#e5e7eb",
            font=("Segoe UI", 10, "bold"),
            padding=(10, 4),
        )
        style.configure(
            "Section.TLabel",
            background="#f5f7fa",
            foreground="#111827",
            font=("Segoe UI", 14, "bold"),
        )
        style.configure(
            "Card.TFrame",
            background="#ffffff",
            bordercolor="#d1d5db",
            relief="solid",
            borderwidth=1,
        )
        style.configure(
            "CardTitle.TLabel",
            background="#ffffff",
            foreground="#111827",
            font=("Segoe UI", 12, "bold"),
        )
        style.configure(
            "MetricValue.TLabel",
            background="#ffffff",
            foreground="#374151",
            font=("Segoe UI", 22, "bold"),
        )
        style.configure(
            "NeutralStatus.TLabel",
            background="#ffffff",
            foreground="#6b7280",
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "Muted.TLabel",
            background="#ffffff",
            foreground="#6b7280",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Overall.TFrame",
            background="#ffffff",
            bordercolor="#d1d5db",
            relief="solid",
            borderwidth=1,
        )
        style.configure(
            "OverallStatus.TLabel",
            background="#ffffff",
            foreground="#6b7280",
            font=("Segoe UI", 18, "bold"),
        )
        for style_name, color in [
            ("OverallHealthyStatus.TLabel", "#15803d"),
            ("OverallWarningStatus.TLabel", "#b45309"),
            ("OverallCriticalStatus.TLabel", "#b91c1c"),
            ("OverallNeutralStatus.TLabel", "#6b7280"),
        ]:
            style.configure(
                style_name,
                background="#ffffff",
                foreground=color,
                font=("Segoe UI", 18, "bold"),
            )
        for style_name, color in [
            ("HealthyStatus.TLabel", "#15803d"),
            ("WarningStatus.TLabel", "#b45309"),
            ("CriticalStatus.TLabel", "#b91c1c"),
            ("InfoStatus.TLabel", "#2563eb"),
            ("ErrorStatus.TLabel", "#b91c1c"),
        ]:
            style.configure(
                style_name,
                background="#ffffff",
                foreground=color,
                font=("Segoe UI", 10, "bold"),
            )
        style.configure(
            "Action.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(10, 8),
        )
        style.configure("Info.TLabel", background="#f5f7fa", foreground="#4b5563")

    def _build_layout(self):
        main_frame = ttk.Frame(self.root, style="App.TFrame", padding=20)
        main_frame.pack(fill="both", expand=True)

        self._build_header(main_frame)

        canvas, content = self._create_scrollable_content(main_frame)
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=1)
        content.rowconfigure(0, weight=1)

        left_panel = ttk.Frame(content, style="App.TFrame")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 16))

        right_panel = ttk.Frame(content, style="App.TFrame")
        right_panel.grid(row=0, column=1, sticky="nsew")

        self._build_system_health(left_panel)
        self._build_service_checks(left_panel)
        self._build_overall_health(right_panel)
        self._build_actions(right_panel)
        canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _create_scrollable_content(self, parent):
        container = ttk.Frame(parent, style="App.TFrame")
        container.pack(fill="both", expand=True, pady=(20, 0))
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        canvas = tk.Canvas(
            container,
            background="#f5f7fa",
            highlightthickness=0,
            borderwidth=0,
        )
        scrollbar = ttk.Scrollbar(
            container,
            orient="vertical",
            command=canvas.yview,
        )
        canvas.configure(yscrollcommand=scrollbar.set)
        self.content_canvas = canvas

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        content = ttk.Frame(canvas, style="App.TFrame")
        content_window = canvas.create_window((0, 0), window=content, anchor="nw")

        content.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(content_window, width=event.width),
        )

        return canvas, content

    def _on_mousewheel(self, event):
        self.root.focus_set()
        self.content_canvas.yview_scroll(int(-event.delta / 120), "units")

    def _build_header(self, parent):
        header = ttk.Frame(parent, style="Header.TFrame", padding=20)
        header.pack(fill="x")
        header.columnconfigure(0, weight=1)

        title_group = ttk.Frame(header, style="Header.TFrame")
        title_group.grid(row=0, column=0, sticky="w")

        ttk.Label(title_group, text="InfraPulse", style="HeaderTitle.TLabel").pack(
            anchor="w"
        )
        ttk.Label(
            title_group,
            text="Infrastructure Health Monitor",
            style="HeaderSubtitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        ttk.Label(header, text="GUI Preview", style="Preview.TLabel").grid(
            row=0,
            column=1,
            sticky="e",
        )

    def _build_system_health(self, parent):
        ttk.Label(parent, text="System Health", style="Section.TLabel").pack(
            anchor="w",
            pady=(0, 10),
        )

        cards = ttk.Frame(parent, style="App.TFrame")
        cards.pack(fill="x")
        for column in range(4):
            cards.columnconfigure(column, weight=1)

        for column, metric in enumerate(["CPU", "Memory", "Disk", "Uptime"]):
            key = metric.lower()
            card = self._create_metric_card(cards, key, metric, "--", "NOT CHECKED")
            card.grid(row=0, column=column, sticky="ew", padx=(0, 10))

    def _build_service_checks(self, parent):
        ttk.Label(parent, text="Service Checks", style="Section.TLabel").pack(
            anchor="w",
            pady=(28, 10),
        )

        self._create_process_card(parent).pack(fill="x", pady=(0, 10))
        self._create_tcp_card(parent).pack(fill="x", pady=(0, 10))
        self._create_http_card(parent).pack(fill="x", pady=(0, 10))

    def _build_overall_health(self, parent):
        ttk.Label(parent, text="Overall Health", style="Section.TLabel").pack(
            anchor="w",
            pady=(0, 10),
        )

        frame = ttk.Frame(parent, style="Overall.TFrame", padding=18)
        frame.pack(fill="x")

        self.overall_status_label = ttk.Label(
            frame,
            textvariable=self.overall_status,
            style="OverallStatus.TLabel",
        )
        self.overall_status_label.pack(anchor="w")
        ttk.Label(
            frame,
            textvariable=self.overall_description,
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(8, 0))

    def _build_actions(self, parent):
        ttk.Label(parent, text="Actions", style="Section.TLabel").pack(
            anchor="w",
            pady=(28, 10),
        )

        actions = ttk.Frame(parent, style="App.TFrame")
        actions.pack(fill="x")

        ttk.Button(
            actions,
            text="Run All Checks",
            style="Action.TButton",
            command=self._run_all_checks,
        ).pack(fill="x", pady=(0, 12))

        buttons = [
            ("Check CPU", self._run_cpu_check),
            ("Check Memory", self._run_memory_check),
            ("Check Disk", self._run_disk_check),
            ("Check Uptime", self._run_uptime_check),
            ("Check Process", self._run_process_check),
            ("Check TCP", self._run_tcp_check),
            ("Check HTTP", self._run_http_check),
        ]
        for label, command in buttons:
            ttk.Button(actions, text=label, command=command).pack(
                fill="x",
                pady=(0, 8),
            )

        ttk.Label(
            parent,
            textvariable=self.status_message,
            style="Info.TLabel",
            wraplength=260,
        ).pack(anchor="w", pady=(12, 0))

    def _create_metric_card(self, parent, key, title, value, status):
        card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        value_var = tk.StringVar(value=value)
        status_var = tk.StringVar(value=status)

        ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(card, textvariable=value_var, style="MetricValue.TLabel").pack(
            anchor="w",
            pady=(14, 6),
        )
        status_label = ttk.Label(
            card,
            textvariable=status_var,
            style=self._get_status_style(status),
        )
        status_label.pack(anchor="w")

        self.metric_cards[key] = {
            "value": value_var,
            "status": status_var,
            "status_label": status_label,
        }
        return card

    def _create_process_card(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        ttk.Label(card, text="Process", style="CardTitle.TLabel").pack(anchor="w")

        self.service_inputs["process_name"] = tk.StringVar(value="explorer.exe")
        self._create_labeled_entry(
            card,
            "Process name",
            self.service_inputs["process_name"],
        )
        ttk.Button(
            card,
            text="Check Process",
            command=self._run_process_check,
        ).pack(anchor="w", pady=(8, 10))

        self._register_service_card(
            "process",
            {
                "target": tk.StringVar(value="Target: --"),
                "detail": tk.StringVar(value="Running: --"),
                "status": tk.StringVar(value="Status: NOT CHECKED"),
            },
            card,
        )
        return card

    def _create_tcp_card(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        ttk.Label(card, text="TCP Port", style="CardTitle.TLabel").pack(anchor="w")

        self.service_inputs["tcp_host"] = tk.StringVar(value="github.com")
        self.service_inputs["tcp_port"] = tk.StringVar(value="443")
        self.service_inputs["tcp_timeout"] = tk.StringVar(value="3")
        self._create_labeled_entry(card, "Host", self.service_inputs["tcp_host"])
        self._create_labeled_entry(card, "Port", self.service_inputs["tcp_port"])
        self._create_labeled_entry(
            card,
            "Timeout",
            self.service_inputs["tcp_timeout"],
        )
        ttk.Label(
            card,
            text="Port: Network service port, such as 443 for HTTPS.",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(2, 8))
        ttk.Button(card, text="Check TCP", command=self._run_tcp_check).pack(
            anchor="w",
            pady=(0, 10),
        )

        self._register_service_card(
            "tcp",
            {
                "target": tk.StringVar(value="Target: --"),
                "detail": tk.StringVar(value="Reachable: --"),
                "status": tk.StringVar(value="Status: NOT CHECKED"),
            },
            card,
        )
        return card

    def _create_http_card(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=16)
        ttk.Label(card, text="HTTP Endpoint", style="CardTitle.TLabel").pack(
            anchor="w"
        )

        self.service_inputs["http_url"] = tk.StringVar(value="https://github.com")
        self.service_inputs["http_timeout"] = tk.StringVar(value="5")
        self._create_labeled_entry(card, "URL", self.service_inputs["http_url"])
        self._create_labeled_entry(
            card,
            "Timeout",
            self.service_inputs["http_timeout"],
        )
        ttk.Button(card, text="Check HTTP", command=self._run_http_check).pack(
            anchor="w",
            pady=(8, 10),
        )

        self._register_service_card(
            "http",
            {
                "target": tk.StringVar(value="Target: --"),
                "detail": tk.StringVar(value="Status Code: --"),
                "extra": tk.StringVar(value="Response Time: --"),
                "status": tk.StringVar(value="Status: NOT CHECKED"),
            },
            card,
        )
        return card

    def _create_labeled_entry(self, parent, label, variable):
        row = ttk.Frame(parent, style="Card.TFrame")
        row.pack(fill="x", pady=(10, 0))
        row.columnconfigure(1, weight=1)

        ttk.Label(row, text=label, style="Muted.TLabel").grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 8),
        )
        ttk.Entry(row, textvariable=variable).grid(row=0, column=1, sticky="ew")

    def _register_service_card(self, key, variables, card):
        labels = {}
        for name, variable in variables.items():
            style = "NeutralStatus.TLabel" if name == "status" else "Muted.TLabel"
            label = ttk.Label(card, textvariable=variable, style=style)
            label.pack(anchor="w", pady=(2, 0))
            labels[f"{name}_label"] = label

        variables.update(labels)
        self.service_cards[key] = variables

    def _get_status_style(self, status):
        status_styles = {
            "HEALTHY": "HealthyStatus.TLabel",
            "WARNING": "WarningStatus.TLabel",
            "CRITICAL": "CriticalStatus.TLabel",
            "INFO": "InfoStatus.TLabel",
            "ERROR": "ErrorStatus.TLabel",
            "NOT CHECKED": "NeutralStatus.TLabel",
        }

        return status_styles.get(status.upper(), "NeutralStatus.TLabel")

    def _get_overall_status_style(self, status):
        status_styles = {
            "HEALTHY": "OverallHealthyStatus.TLabel",
            "WARNING": "OverallWarningStatus.TLabel",
            "CRITICAL": "OverallCriticalStatus.TLabel",
            "NOT CHECKED": "OverallNeutralStatus.TLabel",
        }

        return status_styles.get(status.upper(), "OverallNeutralStatus.TLabel")

    def _store_latest_result(self, key, result):
        self.latest_results[key] = result
        self._update_overall_health()

    def _clear_latest_result(self, key):
        self.latest_results.pop(key, None)
        self._update_overall_health()

    def _update_overall_health(self):
        status_results = [
            result
            for result in self.latest_results.values()
            if result.get("metric") != "uptime" and "status" in result
        ]

        if not status_results:
            overall_status = "not checked"
        else:
            overall_status = calculate_overall_status(status_results)

        display_status = overall_status.upper()
        self.overall_status.set(display_status)
        self.overall_status_label.configure(
            style=self._get_overall_status_style(display_status)
        )
        self.overall_description.set(self._get_overall_description(display_status))

    def _get_overall_description(self, status):
        descriptions = {
            "NOT CHECKED": "Run one or more checks to calculate overall health.",
            "HEALTHY": "All completed checks are healthy.",
            "WARNING": "One or more completed checks require attention.",
            "CRITICAL": "One or more completed checks are critical.",
        }

        return descriptions[status]

    def _update_metric_card(self, key, value, status):
        card = self.metric_cards[key]
        display_status = status.upper()

        card["value"].set(value)
        card["status"].set(display_status)
        card["status_label"].configure(style=self._get_status_style(display_status))

    def _set_metric_error(self, key, check_name, error):
        self._update_metric_card(key, "ERROR", "ERROR")
        self._clear_latest_result(key)
        self.status_message.set(f"{check_name} check failed: {error}")

    def _update_service_card(self, key, target, details, status):
        card = self.service_cards[key]
        display_status = status.upper()

        card["target"].set(f"Target: {target}")
        card["status"].set(f"Status: {display_status}")
        card["status_label"].configure(style=self._get_status_style(display_status))

        if "detail" in card and details:
            card["detail"].set(details[0])
        if "extra" in card and len(details) > 1:
            card["extra"].set(details[1])

    def _set_service_error(self, key, message):
        card = self.service_cards[key]
        card["status"].set("Status: ERROR")
        card["status_label"].configure(style=self._get_status_style("ERROR"))
        self.status_message.set(message)

    def _get_required_text(self, key, message):
        value = self.service_inputs[key].get().strip()
        if not value:
            raise ValueError(message)

        return value

    def _get_tcp_inputs(self):
        host = self._get_required_text("tcp_host", "Invalid TCP host: enter a host.")

        try:
            port = int(self.service_inputs["tcp_port"].get())
        except ValueError as error:
            raise ValueError(
                "Invalid TCP port: enter a value between 1 and 65535."
            ) from error
        if port < 1 or port > 65535:
            raise ValueError("Invalid TCP port: enter a value between 1 and 65535.")

        try:
            timeout = float(self.service_inputs["tcp_timeout"].get())
        except ValueError as error:
            raise ValueError("Invalid TCP timeout: enter a number greater than 0.") from error
        if timeout <= 0:
            raise ValueError("Invalid TCP timeout: enter a number greater than 0.")

        return host, port, timeout

    def _get_http_inputs(self):
        url = self._get_required_text("http_url", "Invalid HTTP URL: enter a URL.")
        if not url.startswith(("http://", "https://")):
            raise ValueError(
                "Invalid HTTP URL: enter a URL starting with http:// or https://."
            )

        try:
            timeout = float(self.service_inputs["http_timeout"].get())
        except ValueError as error:
            raise ValueError(
                "Invalid HTTP timeout: enter a number greater than 0."
            ) from error
        if timeout <= 0:
            raise ValueError("Invalid HTTP timeout: enter a number greater than 0.")

        return url, timeout

    def _run_cpu_check(self):
        try:
            result = check_cpu()
            self._update_metric_card(
                "cpu",
                f"{result['value']}{result['unit']}",
                result["status"],
            )
            self._store_latest_result("cpu", result)
            self.status_message.set("CPU check completed.")
        except Exception as error:  # noqa: BLE001
            self._set_metric_error("cpu", "CPU", error)
            return False

        return True

    def _run_memory_check(self):
        try:
            result = check_memory()
            self._update_metric_card(
                "memory",
                f"{result['value']}{result['unit']}",
                result["status"],
            )
            self._store_latest_result("memory", result)
            self.status_message.set("Memory check completed.")
        except Exception as error:  # noqa: BLE001
            self._set_metric_error("memory", "Memory", error)
            return False

        return True

    def _run_disk_check(self):
        try:
            result = check_disk()
            self._update_metric_card(
                "disk",
                f"{result['value']}{result['unit']}",
                result["status"],
            )
            self._store_latest_result("disk", result)
            self.status_message.set("Disk check completed.")
        except Exception as error:  # noqa: BLE001
            self._set_metric_error("disk", "Disk", error)
            return False

        return True

    def _run_uptime_check(self):
        try:
            result = check_uptime()
            uptime_value = (
                f"{result['days']}d {result['hours']}h {result['minutes']}m"
            )
            self._update_metric_card("uptime", uptime_value, "INFO")
            self._store_latest_result("uptime", result)
            self.status_message.set("Uptime check completed.")
        except Exception as error:  # noqa: BLE001
            self._set_metric_error("uptime", "Uptime", error)
            return False

        return True

    def _run_system_checks(self):
        results = [
            self._run_cpu_check(),
            self._run_memory_check(),
            self._run_disk_check(),
            self._run_uptime_check(),
        ]
        self.status_message.set("System health checks completed.")
        return all(results)

    def _run_process_check(self):
        try:
            process_name = self._get_required_text(
                "process_name",
                "Invalid process name: enter a process name.",
            )
            result = check_process(process_name)
            running = "YES" if result["running"] else "NO"
            self._update_service_card(
                "process",
                result["value"],
                [f"Running: {running}"],
                result["status"],
            )
            self._store_latest_result("process", result)
            self.status_message.set("Process check completed.")
        except ValueError as error:
            self._clear_latest_result("process")
            self._set_service_error("process", str(error))
            return False
        except Exception as error:  # noqa: BLE001
            self._clear_latest_result("process")
            self._set_service_error("process", f"Process check failed: {error}")
            return False

        return True

    def _run_tcp_check(self):
        try:
            host, port, timeout = self._get_tcp_inputs()
            result = check_port(host, port, timeout)
            reachable = "YES" if result["reachable"] else "NO"
            self._update_service_card(
                "tcp",
                f"{result['host']}:{result['value']}",
                [f"Reachable: {reachable}"],
                result["status"],
            )
            self._store_latest_result("tcp_port", result)
            self.status_message.set("TCP check completed.")
        except ValueError as error:
            self._clear_latest_result("tcp_port")
            self._set_service_error("tcp", str(error))
            return False
        except Exception as error:  # noqa: BLE001
            self._clear_latest_result("tcp_port")
            self._set_service_error("tcp", f"TCP check failed: {error}")
            return False

        return True

    def _run_http_check(self):
        try:
            url, timeout = self._get_http_inputs()
            result = check_http(url, timeout)
            response_time = result["response_time_ms"]
            response_time_text = (
                "Response Time: --"
                if response_time is None
                else f"Response Time: {response_time} ms"
            )
            self._update_service_card(
                "http",
                result["url"],
                [
                    f"Status Code: {result['value']}",
                    response_time_text,
                ],
                result["status"],
            )
            self._store_latest_result("http", result)
            self.status_message.set("HTTP check completed.")
        except ValueError as error:
            self._clear_latest_result("http")
            self._set_service_error("http", str(error))
            return False
        except Exception as error:  # noqa: BLE001
            self._clear_latest_result("http")
            self._set_service_error("http", f"HTTP check failed: {error}")
            return False

        return True

    def _run_all_checks(self):
        results = [
            self._run_cpu_check(),
            self._run_memory_check(),
            self._run_disk_check(),
            self._run_uptime_check(),
            self._run_process_check(),
            self._run_tcp_check(),
            self._run_http_check(),
        ]
        if all(results):
            self.status_message.set("All checks completed.")
        else:
            self.status_message.set("Run All completed with one or more issues.")

    def _show_future_phase_message(self):
        self.status_message.set("Check execution will be added in the next phase.")


def main():
    root = tk.Tk()
    InfraPulseGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

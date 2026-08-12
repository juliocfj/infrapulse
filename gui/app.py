import tkinter as tk
from pathlib import Path, PureWindowsPath
from tkinter import filedialog, ttk

import yaml

from infrapulse.checks.cpu import check_cpu
from infrapulse.checks.disk import check_disk
from infrapulse.checks.http import check_http
from infrapulse.checks.memory import check_memory
from infrapulse.checks.port import check_port
from infrapulse.checks.process import check_process
from infrapulse.checks.uptime import check_uptime
from infrapulse.config import load_config, validate_config
from infrapulse.health import calculate_overall_status
from infrapulse.version import __version__

THEMES = {
    "dark": {
        "background": "#0B1120",
        "surface": "#111827",
        "surface_alt": "#182235",
        "input": "#0F172A",
        "border": "#263449",
        "text": "#F8FAFC",
        "muted": "#94A3B8",
        "accent": "#38BDF8",
        "accent_text": "#06111F",
        "button": "#1E293B",
        "button_text": "#E2E8F0",
        "healthy": "#22C55E",
        "healthy_bg": "#052E1A",
        "warning": "#F59E0B",
        "warning_bg": "#3B2605",
        "critical": "#EF4444",
        "critical_bg": "#3B1114",
        "info": "#38BDF8",
        "info_bg": "#082F49",
        "neutral": "#64748B",
        "neutral_bg": "#1E293B",
        "error": "#EF4444",
    },
    "light": {
        "background": "#F4F7FB",
        "surface": "#FFFFFF",
        "surface_alt": "#F8FAFC",
        "input": "#FFFFFF",
        "border": "#D9E2EC",
        "text": "#172033",
        "muted": "#64748B",
        "accent": "#0284C7",
        "accent_text": "#FFFFFF",
        "button": "#E8F1F8",
        "button_text": "#172033",
        "healthy": "#16A34A",
        "healthy_bg": "#DCFCE7",
        "warning": "#D97706",
        "warning_bg": "#FEF3C7",
        "critical": "#DC2626",
        "critical_bg": "#FEE2E2",
        "info": "#0284C7",
        "info_bg": "#E0F2FE",
        "neutral": "#64748B",
        "neutral_bg": "#E2E8F0",
        "error": "#DC2626",
    },
}

DASHBOARD_MAX_WIDTH = 1480


class InfraPulseGUI:
    def __init__(self, root):
        self.root = root
        self.theme_name = tk.StringVar(value="Dark")
        self.theme = THEMES["dark"]
        self.style = None
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
        self.current_config_path = None
        self.current_config_display = tk.StringVar(value="Configuration: Manual")

        self._configure_window()
        self._configure_styles()
        self._build_layout()

    def _configure_window(self):
        self.root.title("InfraPulse")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)

    def _configure_styles(self):
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self._apply_theme()

    def _apply_theme(self):
        theme_key = self.theme_name.get().lower()
        self.theme = THEMES.get(theme_key, THEMES["dark"])
        theme = self.theme
        style = self.style

        self.root.configure(background=theme["background"])

        style.configure("App.TFrame", background=theme["background"])
        style.configure("Header.TFrame", background=theme["surface"])
        style.configure(
            "HeaderTitle.TLabel",
            background=theme["surface"],
            foreground=theme["text"],
            font=("Segoe UI", 22, "bold"),
        )
        style.configure(
            "HeaderSubtitle.TLabel",
            background=theme["surface"],
            foreground=theme["muted"],
            font=("Segoe UI", 11),
        )
        style.configure(
            "HeaderMeta.TLabel",
            background=theme["surface"],
            foreground=theme["muted"],
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "HeaderControl.TLabel",
            background=theme["surface"],
            foreground=theme["muted"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "Section.TLabel",
            background=theme["background"],
            foreground=theme["text"],
            font=("Segoe UI", 13, "bold"),
        )
        style.configure(
            "Card.TFrame",
            background=theme["surface"],
            bordercolor=theme["border"],
            relief="solid",
            borderwidth=1,
        )
        style.configure("CardInner.TFrame", background=theme["surface"])
        style.configure(
            "CardTitle.TLabel",
            background=theme["surface"],
            foreground=theme["text"],
            font=("Segoe UI", 12, "bold"),
        )
        style.configure(
            "MetricValue.TLabel",
            background=theme["surface"],
            foreground=theme["text"],
            font=("Segoe UI", 21, "bold"),
        )
        style.configure(
            "NeutralStatus.TLabel",
            background=theme["neutral_bg"],
            foreground=theme["neutral"],
            font=("Segoe UI", 10, "bold"),
            padding=(8, 3),
        )
        style.configure(
            "Muted.TLabel",
            background=theme["surface"],
            foreground=theme["muted"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "FormLabel.TLabel",
            background=theme["surface"],
            foreground=theme["muted"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "ResultName.TLabel",
            background=theme["surface"],
            foreground=theme["muted"],
            font=("Segoe UI", 9),
        )
        style.configure(
            "ResultValue.TLabel",
            background=theme["surface"],
            foreground=theme["text"],
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "Overall.TFrame",
            background=theme["surface"],
            bordercolor=theme["border"],
            relief="solid",
            borderwidth=1,
        )
        style.configure(
            "OverallStatus.TLabel",
            background=theme["surface"],
            foreground=theme["neutral"],
            font=("Segoe UI", 22, "bold"),
        )
        for style_name, color_key in [
            ("OverallHealthyStatus.TLabel", "healthy"),
            ("OverallWarningStatus.TLabel", "warning"),
            ("OverallCriticalStatus.TLabel", "critical"),
            ("OverallNeutralStatus.TLabel", "neutral"),
        ]:
            style.configure(
                style_name,
                background=theme["surface"],
                foreground=theme[color_key],
                font=("Segoe UI", 22, "bold"),
            )
        for style_name, color_key, background_key in [
            ("HealthyStatus.TLabel", "healthy", "healthy_bg"),
            ("WarningStatus.TLabel", "warning", "warning_bg"),
            ("CriticalStatus.TLabel", "critical", "critical_bg"),
            ("InfoStatus.TLabel", "info", "info_bg"),
            ("ErrorStatus.TLabel", "error", "critical_bg"),
        ]:
            style.configure(
                style_name,
                background=theme[background_key],
                foreground=theme[color_key],
                font=("Segoe UI", 10, "bold"),
                padding=(8, 3),
            )
        style.configure(
            "Action.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(10, 6),
            background=theme["button"],
            foreground=theme["button_text"],
            bordercolor=theme["border"],
            relief="flat",
        )
        style.map(
            "Action.TButton",
            background=[("active", theme["accent"])],
            foreground=[("active", theme["accent_text"])],
        )
        style.configure(
            "TButton",
            font=("Segoe UI", 9),
            padding=(9, 5),
            background=theme["button"],
            foreground=theme["button_text"],
            bordercolor=theme["border"],
            relief="flat",
        )
        style.map(
            "TButton",
            background=[("active", theme["accent"])],
            foreground=[("active", theme["accent_text"])],
        )
        style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            padding=(12, 8),
            background=theme["accent"],
            foreground=theme["accent_text"],
            bordercolor=theme["accent"],
            relief="flat",
        )
        style.map(
            "Primary.TButton",
            background=[("active", theme["accent"])],
            foreground=[("active", theme["accent_text"])],
        )
        style.configure(
            "TEntry",
            fieldbackground=theme["input"],
            foreground=theme["text"],
            insertcolor=theme["text"],
            bordercolor=theme["border"],
            lightcolor=theme["border"],
            darkcolor=theme["border"],
            padding=(7, 5),
        )
        style.map("TEntry", bordercolor=[("focus", theme["accent"])])
        style.configure(
            "TCombobox",
            fieldbackground=theme["input"],
            background=theme["input"],
            foreground=theme["text"],
            arrowcolor=theme["muted"],
            bordercolor=theme["border"],
        )
        style.configure(
            "Vertical.TScrollbar",
            background=theme["surface_alt"],
            troughcolor=theme["background"],
            bordercolor=theme["background"],
            arrowcolor=theme["muted"],
        )
        style.configure("Info.TLabel", background=theme["background"], foreground=theme["muted"])
        style.configure(
            "Activity.TLabel",
            background=theme["surface_alt"],
            foreground=theme["muted"],
            font=("Segoe UI", 9),
            padding=(10, 8),
        )

        if hasattr(self, "content_canvas"):
            self.content_canvas.configure(background=theme["background"])
        self._refresh_status_styles()

    def _change_theme(self, _event=None):
        self._apply_theme()

    def _refresh_status_styles(self):
        for card in self.metric_cards.values():
            status = card["status"].get()
            card["status_label"].configure(style=self._get_status_style(status))

        for card in self.service_cards.values():
            status = card["status"].get().replace("Status: ", "")
            card["status_label"].configure(style=self._get_status_style(status))

        if hasattr(self, "overall_status_label"):
            status = self.overall_status.get()
            self.overall_status_label.configure(
                style=self._get_overall_status_style(status)
            )

    def _build_layout(self):
        main_frame = ttk.Frame(self.root, style="App.TFrame", padding=20)
        main_frame.pack(fill="both", expand=True)

        self._build_header(main_frame)

        canvas, content = self._create_scrollable_content(main_frame)
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)

        dashboard_shell = ttk.Frame(content, style="App.TFrame")
        dashboard_shell.grid(row=0, column=0, sticky="new")
        dashboard_shell.columnconfigure(0, weight=1)

        self._build_system_health(dashboard_shell)

        dashboard = ttk.Frame(dashboard_shell, style="App.TFrame")
        dashboard.pack(fill="both", expand=True)
        dashboard.columnconfigure(0, weight=2, uniform="dashboard")
        dashboard.columnconfigure(1, weight=1, uniform="dashboard")
        dashboard.rowconfigure(0, weight=1)

        left_panel = ttk.Frame(dashboard, style="App.TFrame")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 20))

        right_panel = ttk.Frame(dashboard, style="App.TFrame")
        right_panel.grid(row=0, column=1, sticky="nsew")

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
            background=self.theme["background"],
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
            lambda event: self._resize_scrollable_content(
                canvas,
                content_window,
                event.width,
            ),
        )

        return canvas, content

    def _resize_scrollable_content(self, canvas, content_window, canvas_width):
        content_width = min(canvas_width, DASHBOARD_MAX_WIDTH)
        canvas.itemconfigure(content_window, width=content_width)
        canvas.coords(content_window, max((canvas_width - content_width) // 2, 0), 0)

    def _on_mousewheel(self, event):
        self.root.focus_set()
        self.content_canvas.yview_scroll(int(-event.delta / 120), "units")

    def _build_header(self, parent):
        header = ttk.Frame(parent, style="Header.TFrame", padding=(18, 14))
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

        meta = ttk.Frame(header, style="Header.TFrame")
        meta.grid(
            row=0,
            column=1,
            sticky="e",
        )
        ttk.Label(meta, text="Desktop GUI", style="HeaderMeta.TLabel").grid(
            row=0,
            column=0,
            sticky="e",
            pady=(0, 2),
        )
        ttk.Label(meta, text=f"v{__version__}", style="HeaderControl.TLabel").grid(
            row=1,
            column=0,
            sticky="e",
            pady=(0, 6),
        )
        theme_controls = ttk.Frame(meta, style="Header.TFrame")
        theme_controls.grid(row=2, column=0, sticky="e")
        ttk.Label(theme_controls, text="Theme", style="HeaderControl.TLabel").pack(
            side="left",
            padx=(0, 6),
        )
        theme_combo = ttk.Combobox(
            theme_controls,
            textvariable=self.theme_name,
            values=["Dark", "Light"],
            width=7,
            state="readonly",
        )
        theme_combo.pack(side="left")
        theme_combo.bind("<<ComboboxSelected>>", self._change_theme)

    def _build_system_health(self, parent):
        ttk.Label(parent, text="System Health", style="Section.TLabel").pack(
            anchor="w",
            pady=(0, 10),
        )

        cards = ttk.Frame(parent, style="App.TFrame")
        cards.pack(fill="x", pady=(0, 18))
        for column in range(4):
            cards.columnconfigure(column, weight=1, uniform="system")

        for column, metric in enumerate(["CPU", "Memory", "Disk", "Uptime"]):
            key = metric.lower()
            card = self._create_metric_card(cards, key, metric, "--", "NOT CHECKED")
            padx = (0, 12) if column < 3 else (0, 0)
            card.grid(row=0, column=column, sticky="nsew", padx=padx)

    def _build_service_checks(self, parent):
        ttk.Label(parent, text="Service Checks", style="Section.TLabel").pack(
            anchor="w",
            pady=(0, 10),
        )

        self._create_process_card(parent).pack(fill="x", pady=(0, 10))
        self._create_tcp_card(parent).pack(fill="x", pady=(0, 10))
        self._create_http_card(parent).pack(fill="x", pady=(0, 10))

    def _build_overall_health(self, parent):
        ttk.Label(parent, text="Overall Health", style="Section.TLabel").pack(
            anchor="w",
            pady=(0, 10),
        )

        frame = ttk.Frame(parent, style="Overall.TFrame", padding=16)
        frame.pack(fill="x")
        frame.columnconfigure(0, weight=1)

        self.overall_status_label = ttk.Label(
            frame,
            textvariable=self.overall_status,
            style="OverallStatus.TLabel",
        )
        self.overall_status_label.grid(row=0, column=0, sticky="ew")
        ttk.Label(
            frame,
            textvariable=self.overall_description,
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="ew", pady=(8, 0))

    def _build_actions(self, parent):
        ttk.Label(parent, text="Actions", style="Section.TLabel").pack(
            anchor="w",
            pady=(18, 10),
        )

        actions = ttk.Frame(parent, style="App.TFrame")
        actions.pack(fill="x")
        actions.columnconfigure(0, weight=1)

        ttk.Button(
            actions,
            text="Run All Checks",
            style="Primary.TButton",
            command=self._run_all_checks,
            width=20,
        ).grid(row=0, column=0, pady=(0, 12))

        ttk.Label(parent, text="Configuration", style="Section.TLabel").pack(
            anchor="w",
            pady=(10, 8),
        )
        config_actions = ttk.Frame(parent, style="App.TFrame")
        config_actions.pack(anchor="center")
        ttk.Button(
            config_actions,
            text="Load",
            style="Action.TButton",
            command=self._load_configuration,
            width=10,
        ).pack(side="left", padx=(0, 8), pady=(0, 8))
        ttk.Button(
            config_actions,
            text="Save As",
            style="Action.TButton",
            command=self._save_configuration,
            width=10,
        ).pack(side="left", pady=(0, 8))
        ttk.Label(
            parent,
            textvariable=self.current_config_display,
            style="Info.TLabel",
            wraplength=260,
        ).pack(anchor="center", pady=(0, 14))

        ttk.Label(parent, text="System Checks", style="Section.TLabel").pack(
            anchor="w",
            pady=(8, 8),
        )
        system_buttons = ttk.Frame(parent, style="App.TFrame")
        system_buttons.pack(anchor="center")
        system_buttons.columnconfigure(0, minsize=94)
        system_buttons.columnconfigure(1, minsize=94)

        buttons = [
            ("Check CPU", self._run_cpu_check),
            ("Check Memory", self._run_memory_check),
            ("Check Disk", self._run_disk_check),
            ("Check Uptime", self._run_uptime_check),
        ]
        for index, (label, command) in enumerate(buttons):
            row = index // 2
            column = index % 2
            ttk.Button(
                system_buttons,
                text=label.replace("Check ", ""),
                command=command,
                width=11,
            ).grid(
                row=row,
                column=column,
                sticky="ew",
                padx=4,
                pady=4,
            )

        ttk.Label(parent, text="Status", style="Section.TLabel").pack(
            anchor="w",
            pady=(10, 8),
        )
        ttk.Label(
            parent,
            textvariable=self.status_message,
            style="Activity.TLabel",
            wraplength=260,
        ).pack(anchor="w", fill="x")

    def _create_metric_card(self, parent, key, title, value, status):
        card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        value_var = tk.StringVar(value=value)
        status_var = tk.StringVar(value=status)
        card.grid_propagate(False)
        card.configure(height=112)

        ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(card, textvariable=value_var, style="MetricValue.TLabel").pack(
            anchor="center",
            pady=(10, 8),
        )
        status_label = ttk.Label(
            card,
            textvariable=status_var,
            style=self._get_status_style(status),
        )
        status_label.pack(anchor="center")

        self.metric_cards[key] = {
            "value": value_var,
            "status": status_var,
            "status_label": status_label,
        }
        return card

    def _create_process_card(self, parent):
        card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        ttk.Label(card, text="Process", style="CardTitle.TLabel").pack(anchor="w")

        self.service_inputs["process_name"] = tk.StringVar(value="explorer.exe")
        form = ttk.Frame(card, style="CardInner.TFrame")
        form.pack(anchor="center", pady=(8, 10))
        form.columnconfigure(1, minsize=260)
        self._create_labeled_entry(
            form,
            "Process name",
            self.service_inputs["process_name"],
            width=32,
            side_by_side=True,
        )
        ttk.Button(
            form,
            text="Check Process",
            command=self._run_process_check,
            width=14,
            style="Action.TButton",
        ).grid(row=0, column=2, sticky="w", padx=(10, 0))

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
        card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        ttk.Label(card, text="TCP Port", style="CardTitle.TLabel").pack(anchor="w")

        self.service_inputs["tcp_host"] = tk.StringVar(value="github.com")
        self.service_inputs["tcp_port"] = tk.StringVar(value="443")
        self.service_inputs["tcp_timeout"] = tk.StringVar(value="3")
        form = ttk.Frame(card, style="CardInner.TFrame")
        form.pack(anchor="center", pady=(8, 8))
        self._create_labeled_entry(form, "Host", self.service_inputs["tcp_host"], 30, 0)
        self._create_labeled_entry(form, "Port", self.service_inputs["tcp_port"], 7, 1)
        self._create_labeled_entry(
            form,
            "Timeout",
            self.service_inputs["tcp_timeout"],
            7,
            2,
        )
        ttk.Button(
            form,
            text="Check TCP",
            command=self._run_tcp_check,
            width=12,
            style="Action.TButton",
        ).grid(row=1, column=3, sticky="w", padx=(2, 0), pady=(3, 0))
        ttk.Label(
            card,
            text="Port: Network service port, such as 443 for HTTPS.",
            style="Muted.TLabel",
        ).pack(anchor="center", pady=(0, 8))

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
        card = ttk.Frame(parent, style="Card.TFrame", padding=14)
        ttk.Label(card, text="HTTP Endpoint", style="CardTitle.TLabel").pack(
            anchor="w"
        )

        self.service_inputs["http_url"] = tk.StringVar(value="https://github.com")
        self.service_inputs["http_timeout"] = tk.StringVar(value="5")
        form = ttk.Frame(card, style="CardInner.TFrame")
        form.pack(anchor="center", pady=(8, 10))
        self._create_labeled_entry(form, "URL", self.service_inputs["http_url"], 44, 0)
        self._create_labeled_entry(
            form,
            "Timeout",
            self.service_inputs["http_timeout"],
            7,
            1,
        )
        ttk.Button(
            form,
            text="Check HTTP",
            command=self._run_http_check,
            width=12,
            style="Action.TButton",
        ).grid(row=1, column=2, sticky="w", padx=(2, 0), pady=(3, 0))

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

    def _create_labeled_entry(
        self,
        parent,
        label,
        variable,
        width=28,
        column=0,
        side_by_side=False,
    ):
        if side_by_side:
            ttk.Label(parent, text=label, style="FormLabel.TLabel").grid(
                row=0,
                column=0,
                sticky="w",
                padx=(0, 8),
            )
            ttk.Entry(parent, textvariable=variable, width=width).grid(
                row=0,
                column=1,
                sticky="w",
            )
            return

        group = ttk.Frame(parent, style="CardInner.TFrame")
        group.grid(row=0, column=column, sticky="w", padx=(0, 12))
        ttk.Label(group, text=label, style="FormLabel.TLabel").pack(anchor="w")
        ttk.Entry(group, textvariable=variable, width=width).pack(anchor="w", pady=(3, 0))

    def _register_service_card(self, key, variables, card):
        results = ttk.Frame(card, style="CardInner.TFrame")
        results.pack(anchor="center", fill="x", pady=(4, 0))
        results.columnconfigure(0, weight=1)

        labels = {}
        for name, variable in variables.items():
            style = "NeutralStatus.TLabel" if name == "status" else "Muted.TLabel"
            label = ttk.Label(results, textvariable=variable, style=style)
            label.pack(anchor="center" if name == "status" else "w", pady=(2, 0))
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

    def _reset_service_card(self, key):
        card = self.service_cards[key]
        card["target"].set("Target: --")
        card["status"].set("Status: NOT CHECKED")
        card["status_label"].configure(style=self._get_status_style("NOT CHECKED"))

        details = {
            "process": "Running: --",
            "tcp": "Reachable: --",
            "http": "Status Code: --",
        }
        card["detail"].set(details[key])

        if "extra" in card:
            card["extra"].set("Response Time: --")

    def _reset_service_results(self):
        for result_key in ["process", "tcp_port", "http"]:
            self.latest_results.pop(result_key, None)

        for card_key in ["process", "tcp", "http"]:
            self._reset_service_card(card_key)

        self._update_overall_health()

    def _load_configuration(self):
        path = filedialog.askopenfilename(
            title="Load InfraPulse configuration",
            filetypes=[
                ("YAML files", "*.yaml *.yml"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        try:
            config = load_config(path)
        except (FileNotFoundError, ValueError) as error:
            self.status_message.set(str(error))
            return

        self._apply_configuration(config, path)

    def _get_config_filename(self, path):
        return PureWindowsPath(path).name

    def _apply_configuration(self, config, path):
        processes = config.get("processes", [])
        tcp_targets = config.get("tcp", [])
        http_targets = config.get("http", [])

        if processes:
            self.service_inputs["process_name"].set(processes[0]["name"])
        if tcp_targets:
            self.service_inputs["tcp_host"].set(tcp_targets[0]["host"])
            self.service_inputs["tcp_port"].set(str(tcp_targets[0]["port"]))
            self.service_inputs["tcp_timeout"].set(str(tcp_targets[0]["timeout"]))
        if http_targets:
            self.service_inputs["http_url"].set(http_targets[0]["url"])
            self.service_inputs["http_timeout"].set(str(http_targets[0]["timeout"]))

        self.current_config_path = path
        filename = self._get_config_filename(path)
        self.current_config_display.set(f"Configuration: {filename}")
        self._reset_service_results()

        if any(len(targets) > 1 for targets in [processes, tcp_targets, http_targets]):
            self.status_message.set(
                "Configuration loaded. GUI currently displays the first target "
                "from each target group."
            )
        else:
            self.status_message.set(f"Configuration loaded: {filename}")

    def _save_configuration(self):
        path = filedialog.asksaveasfilename(
            title="Save InfraPulse configuration",
            defaultextension=".yaml",
            initialfile="infrapulse-config.yaml",
            filetypes=[
                ("YAML files", "*.yaml *.yml"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return

        try:
            config = self._build_configuration_from_inputs()
            self._write_configuration(path, config)
        except ValueError as error:
            self.status_message.set(f"Cannot save configuration: {error}")
            return
        except (PermissionError, OSError) as error:
            self.status_message.set(f"Could not save configuration: {error}")
            return

        self.current_config_path = path
        filename = self._get_config_filename(path)
        self.current_config_display.set(f"Configuration: {filename}")
        self.status_message.set(f"Configuration saved: {filename}")

    def _build_configuration_from_inputs(self):
        process_name = self._get_required_text(
            "process_name",
            "Invalid process name: enter a process name.",
        )
        host, port, tcp_timeout = self._get_tcp_inputs()
        url, http_timeout = self._get_http_inputs()

        config = {
            "processes": [{"name": process_name}],
            "tcp": [
                {
                    "host": host,
                    "port": port,
                    "timeout": self._normalize_timeout(tcp_timeout),
                }
            ],
            "http": [
                {
                    "url": url,
                    "timeout": self._normalize_timeout(http_timeout),
                }
            ],
        }
        validate_config(config)

        return config

    def _normalize_timeout(self, timeout):
        if timeout.is_integer():
            return int(timeout)

        return timeout

    def _write_configuration(self, path, config):
        with Path(path).open("w", encoding="utf-8") as config_file:
            yaml.safe_dump(config, config_file, sort_keys=False)

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

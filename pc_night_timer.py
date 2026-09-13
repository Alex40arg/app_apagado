# Version: v0.8

"""Interfaz y temporizador funcional de PC Night Timer."""

import configparser
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import subprocess
import sys
import time
import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk


WINDOW_WIDTH = 850
WINDOW_HEIGHT = 600
TIMER_INTERVAL_MS = 1000
SHUTDOWN_STAGE_DELAY_MS = 1500
GRACEFUL_CLOSE_TIMEOUT_SECONDS = 20
APPLICATION_CLOSE_POLL_MS = 500
FORCED_CLOSE_SETTLE_MS = 1000
FINAL_SHUTDOWN_DELAY_MS = 750
SHUTDOWN_PROCESS_POLL_MS = 100
SW_SHOWNORMAL = 1
SETTINGS_PATH = Path(__file__).resolve().with_name("settings.ini")
MIN_VISIBLE_WINDOW_PIXELS = 80

SHUTDOWN_EXECUTABLE = (
    Path(os.environ.get("SystemRoot", r"C:\Windows"))
    / "System32"
    / "shutdown.exe"
)
SHUTDOWN_COMMAND = (str(SHUTDOWN_EXECUTABLE), "/s", "/f", "/t", "0")

SHUTDOWN_SIMULATION_STAGES = (
    "Preparando apagado...",
    "Cerrando aplicaciones...",
    "Apagando Windows...",
)

WM_CLOSE = 0x0010
GW_OWNER = 4
PROCESS_TERMINATE = 0x0001
SYNCHRONIZE = 0x00100000
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
WAIT_TIMEOUT = 0x00000102
EXPLORER_WINDOW_CLASSES = {"CabinetWClass", "ExploreWClass"}
PROTECTED_PROCESS_NAME_PARTS = (
    "antivirus",
    "avast",
    "avgui",
    "defender",
    "eset",
    "kaspersky",
    "malwarebytes",
    "mcafee",
    "norton",
    "securityhealth",
    "sophos",
)

QUICK_TIMES_MINUTES = {
    "15 min": 15,
    "30 min": 30,
    "45 min": 45,
    "60 min": 60,
    "75 min": 75,
    "90 min": 90,
    "105 min": 105,
    "120 min": 120,
}

DEFAULT_SETTINGS = {
    "General": {
        "last_time_minutes": "60",
        "last_time_option": "60 min",
        "custom_hours": "0",
        "custom_minutes": "2",
    },
    "Window": {"x": "", "y": ""},
    "Testing": {"test_mode": "false"},
}


def is_process_admin():
    """Indica si el proceso actual tiene privilegios elevados en Windows."""
    if os.name != "nt":
        return False
    try:
        is_user_an_admin = ctypes.windll.shell32.IsUserAnAdmin
        is_user_an_admin.restype = wintypes.BOOL
        return bool(is_user_an_admin())
    except (AttributeError, OSError):
        return False


def _elevation_executable():
    """Prefiere el intérprete GUI sin alterar futuros ejecutables empaquetados."""
    current_executable = Path(sys.executable)
    if getattr(sys, "frozen", False):
        return str(current_executable)

    pythonw_executable = current_executable.with_name("pythonw.exe")
    if pythonw_executable.is_file():
        return str(pythonw_executable)
    return str(current_executable)


def relaunch_as_admin():
    """Solicita una nueva instancia elevada y confirma si Windows la inició."""
    if os.name != "nt":
        return False

    if getattr(sys, "frozen", False):
        executable = sys.executable
        arguments = sys.argv[1:]
    else:
        executable = _elevation_executable()
        arguments = [str(Path(__file__).resolve()), *sys.argv[1:]]

    parameters = subprocess.list2cmdline(arguments) if arguments else None
    try:
        shell_execute = ctypes.windll.shell32.ShellExecuteW
        shell_execute.argtypes = [
            wintypes.HWND,
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
            ctypes.c_int,
        ]
        shell_execute.restype = wintypes.HINSTANCE
        result = shell_execute(
            None, "runas", executable, parameters, None, SW_SHOWNORMAL
        )
        return int(result or 0) > 32
    except (AttributeError, OSError, ValueError):
        return False


class WindowsApplicationCloser:
    """Solicita cierre normal y conserva handles para un fallback dirigido."""

    def __init__(self):
        if os.name != "nt":
            raise OSError("El cierre de aplicaciones sólo está disponible en Windows.")

        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._window_callback_type = ctypes.WINFUNCTYPE(
            wintypes.BOOL, wintypes.HWND, wintypes.LPARAM
        )
        self._configure_api()
        self.windows_directory = os.path.normcase(
            os.path.abspath(os.environ.get("WINDIR", r"C:\Windows"))
        )

    def _configure_api(self):
        self.user32.EnumWindows.argtypes = [
            self._window_callback_type,
            wintypes.LPARAM,
        ]
        self.user32.EnumWindows.restype = wintypes.BOOL
        self.user32.IsWindowVisible.argtypes = [wintypes.HWND]
        self.user32.IsWindowVisible.restype = wintypes.BOOL
        self.user32.IsWindow.argtypes = [wintypes.HWND]
        self.user32.IsWindow.restype = wintypes.BOOL
        self.user32.GetWindow.argtypes = [wintypes.HWND, wintypes.UINT]
        self.user32.GetWindow.restype = wintypes.HWND
        self.user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
        self.user32.GetWindowTextLengthW.restype = ctypes.c_int
        self.user32.GetWindowTextW.argtypes = [
            wintypes.HWND,
            wintypes.LPWSTR,
            ctypes.c_int,
        ]
        self.user32.GetWindowTextW.restype = ctypes.c_int
        self.user32.GetClassNameW.argtypes = [
            wintypes.HWND,
            wintypes.LPWSTR,
            ctypes.c_int,
        ]
        self.user32.GetClassNameW.restype = ctypes.c_int
        self.user32.GetWindowThreadProcessId.argtypes = [
            wintypes.HWND,
            ctypes.POINTER(wintypes.DWORD),
        ]
        self.user32.GetWindowThreadProcessId.restype = wintypes.DWORD
        self.user32.PostMessageW.argtypes = [
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        ]
        self.user32.PostMessageW.restype = wintypes.BOOL

        self.kernel32.OpenProcess.argtypes = [
            wintypes.DWORD,
            wintypes.BOOL,
            wintypes.DWORD,
        ]
        self.kernel32.OpenProcess.restype = wintypes.HANDLE
        self.kernel32.QueryFullProcessImageNameW.argtypes = [
            wintypes.HANDLE,
            wintypes.DWORD,
            wintypes.LPWSTR,
            ctypes.POINTER(wintypes.DWORD),
        ]
        self.kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
        self.kernel32.WaitForSingleObject.argtypes = [
            wintypes.HANDLE,
            wintypes.DWORD,
        ]
        self.kernel32.WaitForSingleObject.restype = wintypes.DWORD
        self.kernel32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]
        self.kernel32.TerminateProcess.restype = wintypes.BOOL
        self.kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        self.kernel32.CloseHandle.restype = wintypes.BOOL

    def _window_text(self, window):
        length = self.user32.GetWindowTextLengthW(window)
        if length <= 0:
            return ""
        buffer = ctypes.create_unicode_buffer(length + 1)
        self.user32.GetWindowTextW(window, buffer, len(buffer))
        return buffer.value.strip()

    def _window_class(self, window):
        buffer = ctypes.create_unicode_buffer(256)
        self.user32.GetClassNameW(window, buffer, len(buffer))
        return buffer.value

    def _process_image_path(self, handle):
        buffer = ctypes.create_unicode_buffer(32768)
        size = wintypes.DWORD(len(buffer))
        if not self.kernel32.QueryFullProcessImageNameW(
            handle, 0, buffer, ctypes.byref(size)
        ):
            return ""
        return buffer.value

    def _is_windows_component(self, image_path):
        normalized_path = os.path.normcase(os.path.abspath(image_path))
        try:
            return os.path.commonpath(
                (self.windows_directory, normalized_path)
            ) == self.windows_directory
        except ValueError:
            return True

    @staticmethod
    def _is_protected_name(process_name):
        return any(part in process_name for part in PROTECTED_PROCESS_NAME_PARTS)

    def discover_targets(self):
        windows_by_process = {}
        own_process_id = os.getpid()

        def collect_window(window, _parameter):
            if not self.user32.IsWindowVisible(window):
                return True
            if self.user32.GetWindow(window, GW_OWNER):
                return True
            title = self._window_text(window)
            if not title:
                return True

            process_id = wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(window, ctypes.byref(process_id))
            if not process_id.value or process_id.value == own_process_id:
                return True
            windows_by_process.setdefault(process_id.value, []).append(
                {"window": window, "class_name": self._window_class(window)}
            )
            return True

        callback = self._window_callback_type(collect_window)
        self.user32.EnumWindows(callback, 0)

        targets = []
        for process_id, windows in windows_by_process.items():
            access = (
                SYNCHRONIZE
                | PROCESS_QUERY_LIMITED_INFORMATION
                | PROCESS_TERMINATE
            )
            handle = self.kernel32.OpenProcess(access, False, process_id)
            can_force = bool(handle)
            if not handle:
                access = SYNCHRONIZE | PROCESS_QUERY_LIMITED_INFORMATION
                handle = self.kernel32.OpenProcess(access, False, process_id)
            if not handle:
                continue

            image_path = self._process_image_path(handle)
            process_name = Path(image_path).name.lower() if image_path else ""
            is_explorer = process_name == "explorer.exe"
            if is_explorer:
                windows = [
                    item
                    for item in windows
                    if item["class_name"] in EXPLORER_WINDOW_CLASSES
                ]

            should_skip = (
                not image_path
                or not windows
                or self._is_protected_name(process_name)
                or (self._is_windows_component(image_path) and not is_explorer)
            )
            if should_skip:
                self.kernel32.CloseHandle(handle)
                continue

            targets.append(
                {
                    "pid": process_id,
                    "handle": handle,
                    "process_name": process_name,
                    "windows": [item["window"] for item in windows],
                    "can_force": can_force and not is_explorer,
                    "track_windows": is_explorer,
                }
            )
        return targets

    def request_graceful_close(self, targets):
        for target in targets:
            for window in target["windows"]:
                if self.user32.IsWindow(window):
                    self.user32.PostMessageW(window, WM_CLOSE, 0, 0)

    def pending_targets(self, targets):
        pending = []
        for target in targets:
            if target["track_windows"]:
                if any(self.user32.IsWindow(window) for window in target["windows"]):
                    pending.append(target)
            elif (
                self.kernel32.WaitForSingleObject(target["handle"], 0)
                == WAIT_TIMEOUT
            ):
                pending.append(target)
        return pending

    def force_close(self, targets):
        forced = []
        not_forced = []
        for target in targets:
            if target["can_force"] and self.kernel32.TerminateProcess(
                target["handle"], 1
            ):
                forced.append(target)
            else:
                not_forced.append(target)
        return forced, not_forced

    def release_targets(self, targets):
        for target in targets:
            handle = target.get("handle")
            if handle:
                self.kernel32.CloseHandle(handle)
                target["handle"] = None

COLORS = {
    "background": "#0b111a",
    "panel": "#121b27",
    "panel_alt": "#192534",
    "panel_soft": "#16212e",
    "border": "#2a3a4d",
    "border_soft": "#223143",
    "text": "#f3f7fb",
    "muted": "#98a7b8",
    "muted_dim": "#687789",
    "accent": "#3f93c8",
    "accent_active": "#55a9db",
    "accent_dark": "#173b55",
    "danger": "#7b3542",
    "danger_active": "#964553",
    "danger_soft": "#291820",
    "warning": "#d3a657",
    "warning_panel": "#2a2419",
    "success": "#6eb69a",
    "success_panel": "#142821",
}


def _write_settings(config, path=SETTINGS_PATH):
    try:
        with path.open("w", encoding="utf-8") as settings_file:
            config.write(settings_file)
    except OSError:
        return False
    return True


def _valid_nonnegative_integer(value):
    value = value.strip()
    if not value.isdigit():
        raise ValueError
    return int(value)


def load_settings(path=SETTINGS_PATH):
    """Carga preferencias seguras y conserva claves ajenas de un INI válido."""
    config = configparser.ConfigParser()
    file_exists = path.exists()

    if file_exists:
        try:
            with path.open("r", encoding="utf-8") as settings_file:
                config.read_file(settings_file)
        except (OSError, UnicodeError, configparser.Error):
            config = configparser.ConfigParser()

    stored_time_option = (
        config.get("General", "last_time_option", fallback=None)
        if config.has_section("General")
        else None
    )
    for section, values in DEFAULT_SETTINGS.items():
        if not config.has_section(section):
            config.add_section(section)
        for key, default_value in values.items():
            if not config.has_option(section, key):
                config.set(section, key, default_value)

    option = stored_time_option.strip() if stored_time_option is not None else ""
    valid_options = set(QUICK_TIMES_MINUTES) | {"Personalizado"}
    if option not in valid_options:
        try:
            saved_minutes = int(
                config.get("General", "last_time_minutes", fallback="60").strip()
            )
        except ValueError:
            saved_minutes = 60
        option = next(
            (
                label
                for label, minutes in QUICK_TIMES_MINUTES.items()
                if minutes == saved_minutes
            ),
            "60 min",
        )

    try:
        custom_hours = _valid_nonnegative_integer(
            config.get("General", "custom_hours", fallback="0")
        )
        custom_minutes = _valid_nonnegative_integer(
            config.get("General", "custom_minutes", fallback="2")
        )
        if custom_minutes > 59 or custom_hours * 60 + custom_minutes == 0:
            raise ValueError
    except ValueError:
        custom_hours = 0
        custom_minutes = 2
        if option == "Personalizado":
            option = "60 min"

    try:
        test_mode = config.getboolean("Testing", "test_mode")
    except ValueError:
        test_mode = False

    try:
        window_x = int(config.get("Window", "x").strip())
        window_y = int(config.get("Window", "y").strip())
    except ValueError:
        window_x = None
        window_y = None

    last_time_minutes = (
        custom_hours * 60 + custom_minutes
        if option == "Personalizado"
        else QUICK_TIMES_MINUTES[option]
    )
    config.set("General", "last_time_minutes", str(last_time_minutes))
    config.set("General", "last_time_option", option)
    config.set("General", "custom_hours", str(custom_hours))
    config.set("General", "custom_minutes", str(custom_minutes))
    config.set("Testing", "test_mode", "true" if test_mode else "false")
    config.set("Window", "x", "" if window_x is None else str(window_x))
    config.set("Window", "y", "" if window_y is None else str(window_y))

    if not file_exists:
        _write_settings(config, path)

    return config, {
        "time_option": option,
        "custom_hours": custom_hours,
        "custom_minutes": custom_minutes,
        "test_mode": test_mode,
        "window_x": window_x,
        "window_y": window_y,
    }


class PCNightTimerApp:
    """Controla las vistas y la cuenta regresiva de PC Night Timer."""

    def __init__(self, root, is_admin=None):
        self.root = root
        self.is_admin = is_process_admin() if is_admin is None else bool(is_admin)
        self.settings, saved_settings = load_settings()
        self.test_mode = tk.BooleanVar(value=saved_settings["test_mode"])
        self.quick_time = tk.StringVar(value=saved_settings["time_option"])
        self.hours = tk.StringVar(value=str(saved_settings["custom_hours"]))
        self.minutes = tk.StringVar(value=str(saved_settings["custom_minutes"]))
        self.saved_window_x = saved_settings["window_x"]
        self.saved_window_y = saved_settings["window_y"]
        self.warning_active = False
        self.remaining_seconds = 0
        self.timer_running = False
        self.timer_paused = False
        self.timer_finished = False
        self.timer_after_id = None
        self.shutdown_simulation_active = False
        self.shutdown_stage = 0
        self.shutdown_after_id = None
        self.application_close_active = False
        self.application_close_after_id = None
        self.application_close_started_at = None
        self.application_closer = None
        self.application_close_targets = []
        self.application_close_unresolved = []
        self.windows_shutdown_active = False
        self.windows_shutdown_after_id = None
        self.windows_shutdown_process = None

        self._configure_window()
        self._build_shell()
        self.show_configuration()

    def _configure_window(self):
        self.root.title("PC Night Timer")
        self.root.configure(fg_color=COLORS["background"])
        self.root.resizable(False, False)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        if self._window_position_is_visible(
            self.saved_window_x,
            self.saved_window_y,
            screen_width,
            screen_height,
        ):
            x = self.saved_window_x
            y = self.saved_window_y
        else:
            x = max(0, (screen_width - WINDOW_WIDTH) // 2)
            y = max(0, (screen_height - WINDOW_HEIGHT) // 2)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close_request)

    @staticmethod
    def _window_position_is_visible(x, y, screen_width, screen_height):
        if not isinstance(x, int) or not isinstance(y, int):
            return False
        return (
            x < screen_width - MIN_VISIBLE_WINDOW_PIXELS
            and y < screen_height - MIN_VISIBLE_WINDOW_PIXELS
            and x + WINDOW_WIDTH > MIN_VISIBLE_WINDOW_PIXELS
            and y + WINDOW_HEIGHT > MIN_VISIBLE_WINDOW_PIXELS
        )

    def _build_shell(self):
        self.shell = ctk.CTkFrame(
            self.root, fg_color=COLORS["background"], corner_radius=0
        )
        self.shell.pack(fill="both", expand=True)
        ctk.CTkLabel(
            self.shell,
            text="PC NIGHT TIMER",
            text_color=COLORS["text"],
            font=("Segoe UI Semibold", 30),
        ).pack(pady=(18, 0))
        ctk.CTkLabel(
            self.shell,
            text="Apagado programado simple y visible",
            text_color=COLORS["muted"],
            font=("Segoe UI", 13),
        ).pack(pady=(0, 14))

        self.content = ctk.CTkFrame(
            self.shell,
            width=790,
            height=492,
            fg_color="transparent",
            corner_radius=0,
        )
        self.content.pack(padx=30, pady=(0, 24), fill="both", expand=True)
        self.content.pack_propagate(False)

    def _card(self, *, accent=None):
        border_color = COLORS[accent] if accent else COLORS["border"]
        panel = ctk.CTkFrame(
            self.content,
            fg_color=COLORS["panel"],
            border_color=border_color,
            border_width=1,
            corner_radius=24,
        )
        panel.pack(fill="both", expand=True)
        return panel

    def _clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def _button(self, parent, text, command, *, kind="secondary", width=16):
        palettes = {
            "primary": (COLORS["accent"], COLORS["accent_active"], COLORS["text"]),
            "secondary": (COLORS["panel_alt"], "#233247", COLORS["text"]),
            "danger": (COLORS["danger"], COLORS["danger_active"], COLORS["text"]),
        }
        background, active_background, foreground = palettes[kind]
        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=max(120, width * 10),
            height=54 if kind == "primary" else 50,
            fg_color=background,
            hover_color=active_background,
            text_color=foreground,
            text_color_disabled=COLORS["muted"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["accent"] if kind == "primary" else background,
            font=("Segoe UI Semibold", 22 if kind == "primary" else 22),
            cursor="hand2",
        )
        return button

    def _switch(self, parent):
        return ctk.CTkSwitch(
            parent,
            text="",
            variable=self.test_mode,
            command=self._on_test_mode_changed,
            width=52,
            switch_width=48,
            switch_height=26,
            corner_radius=13,
            fg_color=COLORS["border"],
            progress_color=COLORS["accent"],
            button_color=COLORS["text"],
            button_hover_color="#d9e5f2",
            cursor="hand2",
        )

    def show_configuration(self):
        self.warning_active = False
        self._clear_content()

        panel = self._card()

        ctk.CTkLabel(
            panel,
            text="¿Dentro de cuánto tiempo querés apagar la PC?",
            fg_color="transparent",
            text_color=COLORS["text"],
            font=("Segoe UI Semibold", 23),
        ).pack(pady=(24, 22))

        selector_block = ctk.CTkFrame(panel, fg_color="transparent")
        selector_block.pack()
        ctk.CTkLabel(
            selector_block,
            text="Tiempo rápido",
            fg_color="transparent",
            text_color=COLORS["muted"],
            font=("Segoe UI Semibold", 16),
            anchor="w",
        ).pack(fill="x", pady=(0, 5))

        quick_selector = ctk.CTkComboBox(
            selector_block,
            variable=self.quick_time,
            values=(
                "15 min",
                "30 min",
                "45 min",
                "60 min",
                "75 min",
                "90 min",
                "105 min",
                "120 min",
                "Personalizado",
            ),
            state="readonly",
            width=350,
            height=40,
            fg_color=COLORS["panel_alt"],
            border_color=COLORS["border"],
            button_color=COLORS["panel_alt"],
            button_hover_color="#26354a",
            dropdown_fg_color=COLORS["panel_alt"],
            dropdown_hover_color=COLORS["accent_dark"],
            text_color=COLORS["text"],
            dropdown_text_color=COLORS["text"],
            corner_radius=10,
            font=("Segoe UI Semibold", 15),
            dropdown_font=("Segoe UI", 14),
            command=self._update_custom_state,
        )
        quick_selector.pack()

        # custom_border = ctk.CTkFrame(
        #     panel,
        #     width=440,
        #     height=108,
        #     fg_color=COLORS["border_soft"],
        #     corner_radius=15,
        # )
        # custom_border.pack(pady=(12, 10))
        # custom_border.pack_propagate(False)
        # self.custom_panel = ctk.CTkFrame(
        #     custom_border, fg_color=COLORS["panel_soft"], corner_radius=14
        # )
        # self.custom_panel.pack(fill="both", padx=1, pady=1)

        self.custom_panel = ctk.CTkFrame(
            panel,
            width=440,
            height=120,
            fg_color=COLORS["panel_soft"],
            corner_radius=15,
            )
        self.custom_panel.pack(pady=(18, 14))
        self.custom_panel.pack_propagate(False)



        self.custom_title = ctk.CTkLabel(
            self.custom_panel,
            text="Tiempo personalizado",
            fg_color="transparent",
            text_color=COLORS["muted"],
            font=("Segoe UI Semibold", 16),
            anchor="w",
        )
        self.custom_title.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        self.hours_entry = self._time_entry(self.custom_panel, self.hours)
        self.hours_entry.grid(row=1, column=0, padx=(20, 7), pady=(0, 8))
        hours_label = ctk.CTkLabel(
            self.custom_panel,
            text="horas",
            fg_color="transparent",
            text_color=COLORS["text"],
            font=("Segoe UI", 18),
        )
        hours_label.grid(row=1, column=1, padx=(0, 24))
        self.minutes_entry = self._time_entry(self.custom_panel, self.minutes)
        self.minutes_entry.grid(row=1, column=2, padx=(0, 24), pady=(0, 8))
        minutes_label = ctk.CTkLabel(
            self.custom_panel,
            text="minutos",
            fg_color="transparent",
            text_color=COLORS["text"],
            font=("Segoe UI", 18),
        )
        minutes_label.grid(row=1, column=3, padx=(0, 18))
        self.custom_labels = (self.custom_title, hours_label, minutes_label)

        test_row = ctk.CTkFrame(
            panel,
            width=440,
            height=58,
            fg_color=COLORS["panel_soft"],
            corner_radius=14,
        )
        test_row.pack(pady=(18, 14))
        test_row.pack_propagate(False)
        test_text = ctk.CTkFrame(test_row, fg_color="transparent")
        test_text.pack(side="right", fill="x", expand=True, padx=(8, 16), pady=6)
        ctk.CTkLabel(
            test_text,
            text="Modo de prueba",
            fg_color="transparent",
            text_color=COLORS["text"],
            font=("Segoe UI Semibold", 16),
            anchor="w",
        ).pack(fill="x")
        ctk.CTkLabel(
            test_text,
            text="La PC no se apagará realmente",
            fg_color="transparent",
            text_color=COLORS["muted_dim"],
            font=("Segoe UI", 14),
            anchor="w",
        ).pack(fill="x")
        self.test_switch = self._switch(test_row)
        self.test_switch.pack(side="left", padx=(18, 0))

        self.test_notice = ctk.CTkLabel(
            panel,
            text="",
            fg_color="transparent",
            text_color=COLORS["warning"],
            font=("Segoe UI Semibold", 14),
        )
        self.test_notice.pack(pady=(5, 4))

        self.start_button = self._button(
            panel,
            "INICIAR TIMER",
            self.start_timer,
            kind="primary",
            width=29,
        )
        self.start_button.pack(pady=(0, 5))

        # ctk.CTkLabel(
        #     panel,
        #     text="Acción programada: Apagar PC",
        #     fg_color="transparent",
        #     text_color=COLORS["muted_dim"],
        #     font=("Segoe UI", 14),
        # ).pack()

        self._update_custom_state()
        self._update_test_mode()

    def _time_entry(self, parent, variable):
        return ctk.CTkEntry(
            parent,
            textvariable=variable,
            width=70,
            height=35,
            justify="center",
            fg_color="#101318",
            text_color=COLORS["text"],
            border_color=COLORS["border"],
            border_width=0,
            corner_radius=20,
            font=("Segoe UI Semibold", 18),
        )

    def _update_custom_state(self, _event=None):
        state = "normal" if self.quick_time.get() == "Personalizado" else "disabled"
        self.hours_entry.configure(state=state)
        self.minutes_entry.configure(state=state)
        label_color = COLORS["text"] if state == "normal" else COLORS["muted_dim"]
        entry_color = COLORS["text"] if state == "normal" else COLORS["muted_dim"]
        entry_border = COLORS["accent"] if state == "normal" else COLORS["border_soft"]
        self.hours_entry.configure(text_color=entry_color, border_color=entry_border)
        self.minutes_entry.configure(text_color=entry_color, border_color=entry_border)
        for label in self.custom_labels:
            label.configure(text_color=label_color)
        self.custom_panel.configure(
            fg_color=COLORS["panel_soft"] if state == "normal" else COLORS["panel"],
        )

    def _update_test_mode(self):
        if not hasattr(self, "start_button"):
            return
        if self.test_mode.get():
            self.start_button.configure(text="INICIAR PRUEBA")
            self.test_notice.configure(text="MODO DE PRUEBA — La PC no se apagará")
        else:
            self.start_button.configure(text="INICIAR TIMER")
            self.test_notice.configure(text="")

    def _on_test_mode_changed(self):
        self._update_test_mode()
        self._save_preferences()

    @staticmethod
    def format_time(total_seconds):
        total_seconds = max(0, total_seconds)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _selected_time_seconds(self):
        selection = self.quick_time.get()
        if selection in QUICK_TIMES_MINUTES:
            return QUICK_TIMES_MINUTES[selection] * 60

        if selection != "Personalizado":
            raise ValueError("Seleccioná un tiempo válido.")

        hours_text = self.hours.get().strip()
        minutes_text = self.minutes.get().strip()
        if not hours_text.isdigit() or not minutes_text.isdigit():
            raise ValueError("Ingresá horas y minutos usando solamente números enteros.")

        hours = int(hours_text)
        minutes = int(minutes_text)
        if minutes > 59:
            raise ValueError("Los minutos personalizados deben estar entre 0 y 59.")

        total_seconds = (hours * 60 + minutes) * 60
        if total_seconds == 0:
            raise ValueError("El tiempo personalizado debe ser mayor que cero.")
        return total_seconds

    def start_timer(self):
        if not self.test_mode.get() and not self.is_admin:
            messagebox.showwarning(
                "Permisos de administrador necesarios",
                "PC Night Timer necesita permisos de administrador\n"
                "para garantizar el apagado de Windows.\n\n"
                "Reiniciá la aplicación como administrador.",
                parent=self.root,
            )
            return

        try:
            selected_seconds = self._selected_time_seconds()
        except ValueError as error:
            messagebox.showerror("Tiempo no válido", str(error), parent=self.root)
            return

        self._remember_time_selection(selected_seconds)
        self._save_preferences(remember_time=False)
        self._cancel_scheduled_tick()
        self._cancel_shutdown_simulation()
        self.remaining_seconds = selected_seconds
        self.timer_running = True
        self.timer_paused = False
        self.timer_finished = False
        self.warning_active = selected_seconds <= 60
        self.show_active_timer()
        if self.warning_active:
            self._restore_and_foreground()
        self._schedule_tick()

    def show_active_timer(self):
        self._clear_content()

        panel = self._card(accent="warning" if self.warning_active else None)

        if self.warning_active:
            ctk.CTkLabel(
                panel,
                text=(
                    "PRUEBA — APAGADO SIMULADO"
                    if self.test_mode.get()
                    else "APAGADO INMINENTE"
                ),
                fg_color=COLORS["warning_panel"],
                text_color=COLORS["warning"],
                font=("Segoe UI Semibold", 22),
                height=54,
            ).pack(fill="x")
            description = (
                "La simulación comenzará en menos de un minuto"
                if self.test_mode.get()
                else "La computadora se apagará en menos de un minuto"
            )
        else:
            description = "La PC se apagará en"

        self.timer_description = ctk.CTkLabel(
            panel,
            text=description,
            fg_color="transparent",
            text_color=(
                COLORS["muted"] if not self.warning_active else COLORS["text"]
            ),
            font=("Segoe UI Semibold", 22),
        )
        self.timer_description.pack(
            pady=((28 if self.warning_active else 50), 6)
        )

        self.timer_label = ctk.CTkLabel(
            panel,
            text=self.format_time(self.remaining_seconds),
            fg_color="transparent",
            text_color=(
                COLORS["warning"] if self.warning_active else COLORS["text"]
            ),
            font=("Consolas", 88, "bold"),
        )
        self.timer_label.pack(pady=(0, 3))

        if self.warning_active:
            ctk.CTkLabel(
                panel,
                text=(
                    "MODO DE PRUEBA — La PC no se apagará"
                    if self.test_mode.get()
                    else "Guardá cualquier trabajo pendiente o cancelá el apagado."
                ),
                fg_color="transparent",
                text_color=(
                    COLORS["warning"] if self.test_mode.get() else COLORS["muted"]
                ),
                font=("Segoe UI Semibold" if self.test_mode.get() else "Segoe UI", 22),
            ).pack(pady=(0, 15))
        else:
            mode_text = self._active_status_text()
            self.timer_status = ctk.CTkLabel(
                panel,
                text=mode_text,
                fg_color="transparent",
                text_color=(
                    COLORS["warning"] if self.test_mode.get() else COLORS["muted"]
                ),
                font=("Segoe UI Semibold", 22),
            )
            self.timer_status.pack(pady=(0, 21))

        if self.warning_active:
            self.timer_status = None

        primary_controls = ctk.CTkFrame(panel, fg_color="transparent")
        primary_controls.pack(pady=(0, 15))
        pause_text = "Continuar" if self.timer_paused else "Pausa"
        self.pause_button = self._button(
            primary_controls, pause_text, self.toggle_pause, width=22
        )
        self.pause_button.pack(side="left", padx=8)
        self._button(
            primary_controls,
            "CANCELAR" if self.warning_active else "Cancelar",
            self.cancel_timer,
            kind="danger",
            width=22,
        ).pack(side="left", padx=8)

        add_controls = ctk.CTkFrame(panel, fg_color="transparent")
        add_controls.pack(pady=(0, 12))
        self.add_15_button = self._button(
            add_controls, "+15 min", lambda: self.add_minutes(15), width=18
        )
        self.add_15_button.pack(side="left", padx=8)
        self.add_30_button = self._button(
            add_controls, "+30 min", lambda: self.add_minutes(30), width=18
        )
        self.add_30_button.pack(side="left", padx=8)

        if self.timer_finished:
            self._show_finished_state()

    def _active_status_text(self):
        if self.timer_finished:
            return "Tiempo finalizado"
        if self.timer_paused:
            return "Timer pausado"
        if self.test_mode.get():
            return "MODO DE PRUEBA — La PC no se apagará"
        return "Timer activo"

    def _schedule_tick(self):
        if self.timer_running and not self.timer_paused and self.timer_after_id is None:
            self.timer_after_id = self.root.after(TIMER_INTERVAL_MS, self._tick)

    def _cancel_scheduled_tick(self):
        if self.timer_after_id is not None:
            self.root.after_cancel(self.timer_after_id)
            self.timer_after_id = None

    def _tick(self):
        self.timer_after_id = None
        if not self.timer_running or self.timer_paused:
            return

        self.remaining_seconds = max(0, self.remaining_seconds - 1)
        if self.remaining_seconds <= 60 and not self.warning_active:
            self._enter_final_warning()
        else:
            self.timer_label.configure(text=self.format_time(self.remaining_seconds))
        if self.remaining_seconds == 0:
            self._finish_timer()
        else:
            self._schedule_tick()

    def toggle_pause(self):
        if not self.timer_running:
            return

        if self.timer_paused:
            self.timer_paused = False
            self.pause_button.configure(text="Pausa")
            if self.timer_status is not None:
                self.timer_status.configure(text=self._active_status_text())
            self._schedule_tick()
        else:
            self._cancel_scheduled_tick()
            self.timer_paused = True
            self.pause_button.configure(text="Continuar")
            if self.timer_status is not None:
                self.timer_status.configure(text="Timer pausado")

    def cancel_timer(self):
        self._cancel_scheduled_tick()
        self._cancel_shutdown_simulation()
        self.timer_running = False
        self.timer_paused = False
        self.timer_finished = False
        self.warning_active = False
        self.show_configuration()

    def add_minutes(self, minutes):
        if not self.timer_running:
            return
        self.remaining_seconds += minutes * 60
        if self.warning_active and self.remaining_seconds > 60:
            self.warning_active = False
            self.show_active_timer()
        else:
            self.timer_label.configure(text=self.format_time(self.remaining_seconds))

    def _finish_timer(self):
        self._cancel_scheduled_tick()
        self.remaining_seconds = 0
        self.timer_running = False
        self.timer_paused = False
        self.timer_finished = True
        self.timer_label.configure(text="00:00:00")
        if self.test_mode.get():
            self._start_shutdown_simulation()
        else:
            self._start_application_close()

    def _show_finished_state(self):
        self.timer_description.configure(text="El timer llegó a cero.")
        if self.timer_status is not None:
            self.timer_status.configure(text="Tiempo finalizado")
        self.pause_button.configure(text="Pausa", state="disabled")
        self.add_15_button.configure(state="disabled")
        self.add_30_button.configure(state="disabled")

    def _start_shutdown_simulation(self):
        if self.shutdown_simulation_active:
            return
        self._cancel_scheduled_tick()
        self._cancel_shutdown_simulation()
        self.shutdown_simulation_active = True
        self.shutdown_stage = 0
        self._show_shutdown_simulation_stage()
        self._schedule_shutdown_stage()

    def _show_shutdown_simulation_stage(self):
        self._show_process_screen(
            SHUTDOWN_SIMULATION_STAGES[self.shutdown_stage],
            banner="MODO DE PRUEBA — La PC no se apagará",
            supporting_text="Simulación segura. No se ejecutan acciones del sistema.",
        )

    def _show_process_screen(self, status_text, *, banner=None, supporting_text=None):
        self._clear_content()
        panel = self._card(accent="warning")

        if banner:
            ctk.CTkLabel(
                panel,
                text=banner,
                fg_color=COLORS["warning_panel"],
                text_color=COLORS["warning"],
                font=("Segoe UI Semibold", 12),
                height=42,
            ).pack(fill="x")

        ctk.CTkLabel(
            panel,
            text="00:00:00",
            fg_color="transparent",
            text_color=COLORS["warning"],
            font=("Consolas", 72, "bold"),
        ).pack(pady=((67 if banner else 91), 11))
        ctk.CTkLabel(
            panel,
            text=status_text,
            fg_color="transparent",
            text_color=COLORS["text"],
            font=("Segoe UI Semibold", 22),
        ).pack(pady=(0, 13))
        ctk.CTkLabel(
            panel,
            text=supporting_text or "Cierre seguro en curso. No apagues el equipo manualmente.",
            fg_color="transparent",
            text_color=COLORS["muted"],
            font=("Segoe UI", 10),
        ).pack()

    def _schedule_shutdown_stage(self):
        if self.shutdown_simulation_active and self.shutdown_after_id is None:
            self.shutdown_after_id = self.root.after(
                SHUTDOWN_STAGE_DELAY_MS, self._advance_shutdown_simulation
            )

    def _advance_shutdown_simulation(self):
        self.shutdown_after_id = None
        if not self.shutdown_simulation_active:
            return

        self.shutdown_stage += 1
        if self.shutdown_stage >= len(SHUTDOWN_SIMULATION_STAGES):
            self._complete_shutdown_simulation()
            return
        self._show_shutdown_simulation_stage()
        self._schedule_shutdown_stage()

    def _complete_shutdown_simulation(self):
        self._cancel_shutdown_simulation()
        self.timer_finished = True
        self._clear_content()

        panel = self._card(accent="success")

        ctk.CTkLabel(
            panel,
            text="MODO DE PRUEBA — La PC no se apagó",
            fg_color=COLORS["success_panel"],
            text_color=COLORS["success"],
            font=("Segoe UI Semibold", 12),
            height=42,
        ).pack(fill="x")
        ctk.CTkLabel(
            panel,
            text="✓",
            fg_color="transparent",
            text_color=COLORS["success"],
            font=("Segoe UI", 34),
        ).pack(pady=(50, 4))
        ctk.CTkLabel(
            panel,
            text="PRUEBA COMPLETADA",
            fg_color="transparent",
            text_color=COLORS["text"],
            font=("Segoe UI Semibold", 27),
        ).pack(pady=(0, 12))
        ctk.CTkLabel(
            panel,
            text="El apagado se habría ejecutado correctamente.",
            fg_color="transparent",
            text_color=COLORS["muted"],
            font=("Segoe UI", 13),
        ).pack(pady=(0, 27))
        self._button(
            panel,
            "NUEVO TIMER",
            self._return_to_configuration_after_test,
            kind="primary",
            width=22,
        ).pack()

    def _return_to_configuration_after_test(self):
        self._cancel_shutdown_simulation()
        self.timer_running = False
        self.timer_paused = False
        self.timer_finished = False
        self.warning_active = False
        self.show_configuration()

    def _cancel_shutdown_simulation(self):
        if self.shutdown_after_id is not None:
            try:
                self.root.after_cancel(self.shutdown_after_id)
            except tk.TclError:
                pass
            self.shutdown_after_id = None
        self.shutdown_simulation_active = False

    def _start_application_close(self):
        if self.application_close_active:
            return
        self.application_close_active = True
        self.application_close_unresolved = []
        self._show_application_close_stage("Preparando apagado...")
        self.application_close_after_id = self.root.after(
            0, self._request_application_close
        )

    def _request_application_close(self):
        self.application_close_after_id = None
        if not self.application_close_active:
            return
        self._show_application_close_stage("Cerrando aplicaciones...")
        try:
            self.application_closer = WindowsApplicationCloser()
            self.application_close_targets = (
                self.application_closer.discover_targets()
            )
            self.application_closer.request_graceful_close(
                self.application_close_targets
            )
        except OSError:
            self.application_close_unresolved = ["Plataforma no compatible"]
            self._complete_application_close()
            return

        if not self.application_close_targets:
            self._complete_application_close()
            return

        self.application_close_started_at = time.monotonic()
        self._show_application_close_stage("Esperando cierre ordenado...")
        self._schedule_application_close_poll()

    def _schedule_application_close_poll(self):
        if self.application_close_active and self.application_close_after_id is None:
            self.application_close_after_id = self.root.after(
                APPLICATION_CLOSE_POLL_MS, self._poll_application_close
            )

    def _poll_application_close(self):
        self.application_close_after_id = None
        if not self.application_close_active or self.application_closer is None:
            return

        pending = self.application_closer.pending_targets(
            self.application_close_targets
        )
        if not pending:
            self._complete_application_close()
            return

        elapsed = time.monotonic() - self.application_close_started_at
        if elapsed < GRACEFUL_CLOSE_TIMEOUT_SECONDS:
            self._schedule_application_close_poll()
            return

        self._show_application_close_stage("Forzando aplicaciones pendientes...")
        _forced, self.application_close_unresolved = (
            self.application_closer.force_close(pending)
        )
        self.application_close_after_id = self.root.after(
            FORCED_CLOSE_SETTLE_MS, self._finish_forced_application_close
        )

    def _finish_forced_application_close(self):
        self.application_close_after_id = None
        if not self.application_close_active or self.application_closer is None:
            return
        still_pending = self.application_closer.pending_targets(
            self.application_close_targets
        )
        unresolved_ids = {target["pid"] for target in self.application_close_unresolved}
        self.application_close_unresolved = [
            target
            for target in still_pending
            if target["pid"] in unresolved_ids or target["can_force"]
        ]
        self._complete_application_close()

    def _show_application_close_stage(self, status_text):
        self._show_process_screen(status_text)

    def _complete_application_close(self):
        self._cancel_application_close()
        self.timer_finished = True
        self._save_preferences()
        self.windows_shutdown_active = True
        self._show_application_close_stage("Apagando Windows...")
        self.windows_shutdown_after_id = self.root.after(
            FINAL_SHUTDOWN_DELAY_MS, self._launch_windows_shutdown
        )

    def _launch_windows_shutdown(self):
        self.windows_shutdown_after_id = None
        if not self.windows_shutdown_active:
            return
        if self.test_mode.get():
            self._show_windows_shutdown_error(
                "El Modo de prueba impidió ejecutar el apagado real."
            )
            return
        if not self.is_admin:
            self._show_windows_shutdown_error(
                "PC Night Timer no tiene permisos de administrador."
            )
            return

        try:
            self.windows_shutdown_process = subprocess.Popen(
                SHUTDOWN_COMMAND,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except (OSError, ValueError) as error:
            self._show_windows_shutdown_error(str(error))
            return

        self.windows_shutdown_after_id = self.root.after(
            SHUTDOWN_PROCESS_POLL_MS, self._check_windows_shutdown_process
        )

    def _check_windows_shutdown_process(self):
        self.windows_shutdown_after_id = None
        if not self.windows_shutdown_active or self.windows_shutdown_process is None:
            return

        return_code = self.windows_shutdown_process.poll()
        if return_code is None:
            self.windows_shutdown_after_id = self.root.after(
                SHUTDOWN_PROCESS_POLL_MS, self._check_windows_shutdown_process
            )
            return
        if return_code != 0:
            self._show_windows_shutdown_error(
                f"shutdown.exe terminó con el código de error {return_code}."
            )
            return

        self.windows_shutdown_active = False
        self.windows_shutdown_process = None
        self.root.destroy()

    def _show_windows_shutdown_error(self, detail):
        self._cancel_windows_shutdown()
        self._clear_content()

        panel = self._card(accent="danger")
        ctk.CTkLabel(
            panel,
            text="ERROR DE APAGADO",
            fg_color=COLORS["danger_soft"],
            text_color="#d88895",
            font=("Segoe UI Semibold", 12),
            height=42,
        ).pack(fill="x")
        ctk.CTkLabel(
            panel,
            text="NO SE PUDO INICIAR EL APAGADO",
            fg_color="transparent",
            text_color=COLORS["text"],
            font=("Segoe UI Semibold", 23),
        ).pack(pady=(61, 15))
        ctk.CTkLabel(
            panel,
            text=(
                "Windows permanece encendido.\n\n"
                f"Detalle: {detail}"
            ),
            fg_color="transparent",
            text_color=COLORS["muted"],
            font=("Segoe UI", 12),
            justify="center",
            wraplength=650,
        ).pack(pady=(0, 30))

        controls = ctk.CTkFrame(panel, fg_color="transparent")
        controls.pack()
        self._button(
            controls,
            "VOLVER A CONFIGURACIÓN",
            self._return_after_shutdown_error,
            kind="primary",
            width=24,
        ).pack(side="left", padx=7)
        self._button(
            controls,
            "CERRAR",
            self.root.destroy,
            kind="secondary",
            width=14,
        ).pack(side="left", padx=7)

    def _return_after_shutdown_error(self):
        self.timer_finished = False
        self.warning_active = False
        self.show_configuration()

    def _cancel_windows_shutdown(self):
        if self.windows_shutdown_after_id is not None:
            try:
                self.root.after_cancel(self.windows_shutdown_after_id)
            except tk.TclError:
                pass
            self.windows_shutdown_after_id = None
        self.windows_shutdown_active = False
        self.windows_shutdown_process = None

    def _cancel_application_close(self):
        if self.application_close_after_id is not None:
            try:
                self.root.after_cancel(self.application_close_after_id)
            except tk.TclError:
                pass
            self.application_close_after_id = None
        if self.application_closer is not None:
            self.application_closer.release_targets(self.application_close_targets)
        self.application_close_targets = []
        self.application_closer = None
        self.application_close_started_at = None
        self.application_close_active = False

    def _enter_final_warning(self):
        if self.warning_active or not self.timer_running:
            return
        self.warning_active = True
        self.show_active_timer()
        self._restore_and_foreground()

    def _restore_and_foreground(self):
        window_state = self.root.state()
        if window_state in ("iconic", "withdrawn"):
            self.root.deiconify()
        elif window_state == "zoomed":
            self.root.state("normal")

        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after_idle(self._release_topmost)
        self.root.focus_force()

    def _release_topmost(self):
        try:
            self.root.attributes("-topmost", False)
        except tk.TclError:
            pass

    def _remember_time_selection(self, selected_seconds=None):
        if selected_seconds is None:
            try:
                selected_seconds = self._selected_time_seconds()
            except ValueError:
                return False

        selection = self.quick_time.get()
        self.settings.set(
            "General", "last_time_minutes", str(selected_seconds // 60)
        )
        self.settings.set("General", "last_time_option", selection)
        if selection == "Personalizado":
            self.settings.set("General", "custom_hours", self.hours.get().strip())
            self.settings.set("General", "custom_minutes", self.minutes.get().strip())
        return True

    def _remember_window_position(self):
        if self.root.state() != "normal":
            return

        x = self.root.winfo_x()
        y = self.root.winfo_y()
        if self._window_position_is_visible(
            x,
            y,
            self.root.winfo_screenwidth(),
            self.root.winfo_screenheight(),
        ):
            self.settings.set("Window", "x", str(x))
            self.settings.set("Window", "y", str(y))

    def _save_preferences(self, remember_time=True):
        if remember_time:
            self._remember_time_selection()
        self.settings.set(
            "Testing", "test_mode", "true" if self.test_mode.get() else "false"
        )
        self._remember_window_position()
        _write_settings(self.settings)

    def _on_close_request(self):
        if self.windows_shutdown_active:
            if self.windows_shutdown_process is not None:
                self._cancel_windows_shutdown()
                self.root.destroy()
            return

        if self.application_close_active:
            self._cancel_scheduled_tick()
            self._cancel_application_close()
            self._save_preferences()
            self.root.destroy()
            return

        if self.shutdown_simulation_active:
            self._cancel_scheduled_tick()
            self._cancel_shutdown_simulation()
            self._save_preferences()
            self.root.destroy()
            return

        if not self.timer_running:
            self._cancel_shutdown_simulation()
            self._save_preferences()
            self.root.destroy()
            return

        should_close = messagebox.askyesno(
            "Cerrar PC Night Timer",
            "Hay un temporizador activo.\n\n"
            "Si cerrás PC Night Timer, el apagado programado se cancelará.\n\n"
            "¿Querés cerrar la aplicación?",
            icon="warning",
            parent=self.root,
        )
        if should_close:
            self._cancel_scheduled_tick()
            self._cancel_shutdown_simulation()
            self.timer_running = False
            self.timer_paused = False
            self._save_preferences()
            self.root.destroy()


def main():
    is_admin = is_process_admin()
    if not is_admin and relaunch_as_admin():
        return

    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    PCNightTimerApp(root, is_admin=is_admin)
    root.mainloop()


if __name__ == "__main__":
    main()

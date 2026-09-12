# Version: v0.5

"""Interfaz y temporizador funcional de PC Night Timer."""

import configparser
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


WINDOW_WIDTH = 850
WINDOW_HEIGHT = 600
TIMER_INTERVAL_MS = 1000
SHUTDOWN_STAGE_DELAY_MS = 1500
SETTINGS_PATH = Path(__file__).resolve().with_name("settings.ini")
MIN_VISIBLE_WINDOW_PIXELS = 80

SHUTDOWN_SIMULATION_STAGES = (
    "Preparando apagado...",
    "Cerrando aplicaciones...",
    "Apagando Windows...",
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

COLORS = {
    "background": "#0d0f12",
    "panel": "#171a1f",
    "panel_alt": "#20242a",
    "text": "#f0f2f5",
    "muted": "#b0b6bf",
    "accent": "#4f6f8f",
    "accent_active": "#5e82a7",
    "danger": "#7a3038",
    "danger_active": "#91404a",
    "warning": "#c99b4a",
    "warning_panel": "#2b2418",
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

    def __init__(self, root):
        self.root = root
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

        self._configure_window()
        self._configure_styles()
        self._build_shell()
        self.show_configuration()

    def _configure_window(self):
        self.root.title("PC Night Timer")
        self.root.configure(background=COLORS["background"])
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

    def _configure_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure(
            "TCombobox",
            fieldbackground=COLORS["panel_alt"],
            background=COLORS["panel_alt"],
            foreground=COLORS["text"],
            arrowcolor=COLORS["text"],
            bordercolor=COLORS["accent"],
            lightcolor=COLORS["accent"],
            darkcolor=COLORS["accent"],
            padding=8,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", COLORS["panel_alt"])],
            foreground=[("readonly", COLORS["text"])],
            selectbackground=[("readonly", COLORS["panel_alt"])],
            selectforeground=[("readonly", COLORS["text"])],
        )
        style.configure(
            "Night.TCheckbutton",
            background=COLORS["panel"],
            foreground=COLORS["text"],
            font=("Segoe UI", 13),
            padding=6,
        )
        style.map(
            "Night.TCheckbutton",
            background=[("active", COLORS["panel"])],
            foreground=[("active", COLORS["text"])],
            indicatorcolor=[
                ("selected", COLORS["accent"]),
                ("!selected", COLORS["panel_alt"]),
            ],
        )

    def _build_shell(self):
        header = tk.Frame(self.root, bg=COLORS["background"], height=92)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="PC NIGHT TIMER",
            bg=COLORS["background"],
            fg=COLORS["text"],
            font=("Segoe UI Semibold", 25),
            takefocus=False,
        ).pack(pady=(23, 0))
        tk.Label(
            header,
            text="Apagado programado simple y visible",
            bg=COLORS["background"],
            fg=COLORS["muted"],
            font=("Segoe UI", 11),
            takefocus=False,
        ).pack(pady=(2, 0))

        self.content = tk.Frame(self.root, bg=COLORS["background"])
        self.content.pack(fill="both", expand=True, padx=32, pady=(2, 25))

    def _clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def _button(self, parent, text, command, *, kind="secondary", width=16):
        palettes = {
            "primary": (COLORS["accent"], COLORS["accent_active"], COLORS["text"]),
            "secondary": (COLORS["panel_alt"], "#2b3038", COLORS["text"]),
            "danger": (COLORS["danger"], COLORS["danger_active"], COLORS["text"]),
        }
        background, active_background, foreground = palettes[kind]
        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            bg=background,
            activebackground=active_background,
            fg=foreground,
            activeforeground=foreground,
            disabledforeground=COLORS["muted"],
            relief="flat",
            bd=0,
            font=("Segoe UI Semibold", 12),
            cursor="hand2",
            padx=10,
            pady=10,
            takefocus=True,
        )

    def show_configuration(self):
        self.warning_active = False
        self._clear_content()

        panel = tk.Frame(
            self.content,
            bg=COLORS["panel"],
            highlightthickness=1,
            highlightbackground="#292e35",
        )
        panel.pack(fill="both", expand=True)

        tk.Label(
            panel,
            text="¿Dentro de cuánto tiempo querés apagar la PC?",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI Semibold", 17),
            takefocus=False,
        ).pack(pady=(24, 18))

        selector_row = tk.Frame(panel, bg=COLORS["panel"])
        selector_row.pack()
        tk.Label(
            selector_row,
            text="Tiempo rápido",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 12),
            takefocus=False,
        ).pack(side="left", padx=(0, 14))

        quick_selector = ttk.Combobox(
            selector_row,
            textvariable=self.quick_time,
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
            width=20,
            font=("Segoe UI", 13),
        )
        quick_selector.pack(side="left")
        quick_selector.bind("<<ComboboxSelected>>", self._update_custom_state)

        custom_panel = tk.Frame(panel, bg=COLORS["panel_alt"], padx=22, pady=13)
        custom_panel.pack(pady=(18, 15))
        tk.Label(
            custom_panel,
            text="Tiempo personalizado",
            bg=COLORS["panel_alt"],
            fg=COLORS["muted"],
            font=("Segoe UI Semibold", 11),
            takefocus=False,
        ).grid(row=0, column=0, columnspan=4, pady=(0, 9))

        self.hours_entry = self._time_entry(custom_panel, self.hours)
        self.hours_entry.grid(row=1, column=0, padx=(0, 7))
        tk.Label(
            custom_panel,
            text="horas",
            bg=COLORS["panel_alt"],
            fg=COLORS["text"],
            font=("Segoe UI", 12),
            takefocus=False,
        ).grid(row=1, column=1, padx=(0, 24))
        self.minutes_entry = self._time_entry(custom_panel, self.minutes)
        self.minutes_entry.grid(row=1, column=2, padx=(0, 7))
        tk.Label(
            custom_panel,
            text="minutos",
            bg=COLORS["panel_alt"],
            fg=COLORS["text"],
            font=("Segoe UI", 12),
            takefocus=False,
        ).grid(row=1, column=3)

        test_check = ttk.Checkbutton(
            panel,
            text="Modo de prueba",
            variable=self.test_mode,
            command=self._on_test_mode_changed,
            style="Night.TCheckbutton",
            takefocus=True,
        )
        test_check.pack()

        self.test_notice = tk.Label(
            panel,
            text="",
            bg=COLORS["panel"],
            fg=COLORS["warning"],
            font=("Segoe UI Semibold", 10),
            takefocus=False,
        )
        self.test_notice.pack(pady=(0, 9))

        self.start_button = self._button(
            panel,
            "INICIAR TIMER",
            self.start_timer,
            kind="primary",
            width=25,
        )
        self.start_button.pack(pady=(1, 10))

        tk.Label(
            panel,
            text="Acción programada: Apagar PC",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 10),
            takefocus=False,
        ).pack()

        self._update_custom_state()
        self._update_test_mode()

    def _time_entry(self, parent, variable):
        return tk.Entry(
            parent,
            textvariable=variable,
            width=4,
            justify="center",
            bg="#101318",
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            disabledbackground="#181b20",
            disabledforeground="#727984",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#3a414b",
            highlightcolor=COLORS["accent"],
            font=("Segoe UI Semibold", 14),
            takefocus=True,
        )

    def _update_custom_state(self, _event=None):
        state = "normal" if self.quick_time.get() == "Personalizado" else "disabled"
        self.hours_entry.configure(state=state)
        self.minutes_entry.configure(state=state)

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

        panel = tk.Frame(
            self.content,
            bg=COLORS["panel"],
            highlightthickness=2,
            highlightbackground=(
                COLORS["warning"] if self.warning_active else "#292e35"
            ),
        )
        panel.pack(fill="both", expand=True)

        if self.warning_active:
            tk.Label(
                panel,
                text=(
                    "PRUEBA — APAGADO SIMULADO"
                    if self.test_mode.get()
                    else "APAGADO INMINENTE"
                ),
                bg=COLORS["warning_panel"],
                fg=COLORS["warning"],
                font=("Segoe UI Semibold", 14),
                pady=9,
                takefocus=False,
            ).pack(fill="x")
            description = (
                "La simulación comenzará en menos de un minuto"
                if self.test_mode.get()
                else "La computadora se apagará en menos de un minuto"
            )
        else:
            description = "La PC se apagará en"

        self.timer_description = tk.Label(
            panel,
            text=description,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI Semibold", 18),
            takefocus=False,
        )
        self.timer_description.pack(
            pady=((22 if self.warning_active else 35), 4)
        )

        self.timer_label = tk.Label(
            panel,
            text=self.format_time(self.remaining_seconds),
            bg=COLORS["panel"],
            fg=COLORS["warning"] if self.warning_active else COLORS["text"],
            font=("Consolas", 68, "bold"),
            takefocus=False,
        )
        self.timer_label.pack(pady=(0, 5))

        if self.warning_active:
            tk.Label(
                panel,
                text=(
                    "MODO DE PRUEBA — La PC no se apagará"
                    if self.test_mode.get()
                    else "Guardá cualquier trabajo pendiente o cancelá el apagado."
                ),
                bg=COLORS["panel"],
                fg=COLORS["warning"] if self.test_mode.get() else COLORS["muted"],
                font=("Segoe UI Semibold" if self.test_mode.get() else "Segoe UI", 12),
                takefocus=False,
            ).pack(pady=(0, 12))
        else:
            mode_text = self._active_status_text()
            self.timer_status = tk.Label(
                panel,
                text=mode_text,
                bg=COLORS["panel"],
                fg=COLORS["warning"] if self.test_mode.get() else COLORS["muted"],
                font=("Segoe UI Semibold", 11),
                takefocus=False,
            )
            self.timer_status.pack(pady=(0, 16))

        if self.warning_active:
            self.timer_status = None

        primary_controls = tk.Frame(panel, bg=COLORS["panel"])
        primary_controls.pack(pady=(0, 13))
        pause_text = "Continuar" if self.timer_paused else "Pausa"
        self.pause_button = self._button(
            primary_controls, pause_text, self.toggle_pause
        )
        self.pause_button.pack(side="left", padx=7)
        self._button(
            primary_controls,
            "CANCELAR" if self.warning_active else "Cancelar",
            self.cancel_timer,
            kind="danger",
        ).pack(side="left", padx=7)

        add_controls = tk.Frame(panel, bg=COLORS["panel"])
        add_controls.pack(pady=(0, 12))
        self.add_15_button = self._button(
            add_controls, "+15 min", lambda: self.add_minutes(15), width=12
        )
        self.add_15_button.pack(side="left", padx=7)
        self.add_30_button = self._button(
            add_controls, "+30 min", lambda: self.add_minutes(30), width=12
        )
        self.add_30_button.pack(side="left", padx=7)

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
            self._show_finished_state()

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
        self._clear_content()

        panel = tk.Frame(
            self.content,
            bg=COLORS["panel"],
            highlightthickness=2,
            highlightbackground=COLORS["warning"],
        )
        panel.pack(fill="both", expand=True)

        tk.Label(
            panel,
            text="MODO DE PRUEBA — La PC no se apagará",
            bg=COLORS["warning_panel"],
            fg=COLORS["warning"],
            font=("Segoe UI Semibold", 14),
            pady=9,
            takefocus=False,
        ).pack(fill="x")
        tk.Label(
            panel,
            text="00:00:00",
            bg=COLORS["panel"],
            fg=COLORS["warning"],
            font=("Consolas", 68, "bold"),
            takefocus=False,
        ).pack(pady=(68, 14))
        tk.Label(
            panel,
            text=SHUTDOWN_SIMULATION_STAGES[self.shutdown_stage],
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI Semibold", 22),
            takefocus=False,
        ).pack(pady=(0, 16))
        tk.Label(
            panel,
            text="Simulación segura. No se ejecutan acciones del sistema.",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 11),
            takefocus=False,
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

        panel = tk.Frame(
            self.content,
            bg=COLORS["panel"],
            highlightthickness=2,
            highlightbackground=COLORS["accent"],
        )
        panel.pack(fill="both", expand=True)

        tk.Label(
            panel,
            text="MODO DE PRUEBA — La PC no se apagó",
            bg=COLORS["panel_alt"],
            fg=COLORS["warning"],
            font=("Segoe UI Semibold", 13),
            pady=9,
            takefocus=False,
        ).pack(fill="x")
        tk.Label(
            panel,
            text="PRUEBA COMPLETADA",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI Semibold", 28),
            takefocus=False,
        ).pack(pady=(105, 18))
        tk.Label(
            panel,
            text="El apagado se habría ejecutado correctamente.",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Segoe UI", 14),
            takefocus=False,
        ).pack(pady=(0, 30))
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
    root = tk.Tk()
    PCNightTimerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

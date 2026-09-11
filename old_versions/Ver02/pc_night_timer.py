# Version: v0.2

"""Interfaz y temporizador funcional de PC Night Timer."""

import tkinter as tk
from tkinter import messagebox, ttk


WINDOW_WIDTH = 850
WINDOW_HEIGHT = 600
TIMER_INTERVAL_MS = 1000

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


class PCNightTimerApp:
    """Controla las vistas y la cuenta regresiva de PC Night Timer."""

    def __init__(self, root):
        self.root = root
        self.test_mode = tk.BooleanVar(value=False)
        self.quick_time = tk.StringVar(value="60 min")
        self.hours = tk.StringVar(value="0")
        self.minutes = tk.StringVar(value="2")
        self.warning_preview = False
        self.remaining_seconds = 0
        self.timer_running = False
        self.timer_paused = False
        self.timer_finished = False
        self.timer_after_id = None

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
        x = max(0, (screen_width - WINDOW_WIDTH) // 2)
        y = max(0, (screen_height - WINDOW_HEIGHT) // 2)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

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
        self.warning_preview = False
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
            command=self._update_test_mode,
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

        self._cancel_scheduled_tick()
        self.remaining_seconds = selected_seconds
        self.timer_running = True
        self.timer_paused = False
        self.timer_finished = False
        self.warning_preview = False
        self.show_active_timer()
        self._schedule_tick()

    def show_active_timer(self):
        self._clear_content()

        panel = tk.Frame(
            self.content,
            bg=COLORS["panel"],
            highlightthickness=2,
            highlightbackground=(
                COLORS["warning"] if self.warning_preview else "#292e35"
            ),
        )
        panel.pack(fill="both", expand=True)

        if self.warning_preview:
            tk.Label(
                panel,
                text="APAGADO INMINENTE",
                bg=COLORS["warning_panel"],
                fg=COLORS["warning"],
                font=("Segoe UI Semibold", 14),
                pady=9,
                takefocus=False,
            ).pack(fill="x")
            description = "La computadora se apagará en menos de un minuto"
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
            pady=((22 if self.warning_preview else 35), 4)
        )

        self.timer_label = tk.Label(
            panel,
            text=self.format_time(self.remaining_seconds),
            bg=COLORS["panel"],
            fg=COLORS["warning"] if self.warning_preview else COLORS["text"],
            font=("Consolas", 68, "bold"),
            takefocus=False,
        )
        self.timer_label.pack(pady=(0, 5))

        if self.warning_preview:
            tk.Label(
                panel,
                text="Guardá cualquier trabajo pendiente o cancelá el apagado.",
                bg=COLORS["panel"],
                fg=COLORS["muted"],
                font=("Segoe UI", 12),
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

        if self.warning_preview:
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
            "CANCELAR" if self.warning_preview else "Cancelar",
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

        preview_text = "VOLVER A VISTA NORMAL" if self.warning_preview else "VER ADVERTENCIA FINAL"
        preview_button = tk.Button(
            panel,
            text=preview_text,
            command=self._toggle_warning_preview,
            bg=COLORS["panel"],
            activebackground=COLORS["panel"],
            fg=COLORS["muted"],
            activeforeground=COLORS["text"],
            relief="flat",
            bd=0,
            font=("Segoe UI", 9, "underline"),
            cursor="hand2",
            takefocus=True,
        )
        preview_button.pack()

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
        self.timer_running = False
        self.timer_paused = False
        self.timer_finished = False
        self.warning_preview = False
        self.show_configuration()

    def add_minutes(self, minutes):
        if not self.timer_running:
            return
        self.remaining_seconds += minutes * 60
        self.timer_label.configure(text=self.format_time(self.remaining_seconds))

    def _finish_timer(self):
        self._cancel_scheduled_tick()
        self.remaining_seconds = 0
        self.timer_running = False
        self.timer_paused = False
        self.timer_finished = True
        self.timer_label.configure(text="00:00:00")
        self._show_finished_state()

    def _show_finished_state(self):
        self.timer_description.configure(text="El timer llegó a cero.")
        if self.timer_status is not None:
            self.timer_status.configure(text="Tiempo finalizado")
        self.pause_button.configure(text="Pausa", state="disabled")
        self.add_15_button.configure(state="disabled")
        self.add_30_button.configure(state="disabled")

    def _toggle_warning_preview(self):
        self.warning_preview = not self.warning_preview
        self.show_active_timer()


def main():
    root = tk.Tk()
    PCNightTimerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

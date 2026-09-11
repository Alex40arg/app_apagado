# Version: v0.1

"""Interfaz estática inicial de PC Night Timer."""

import tkinter as tk
from tkinter import ttk


WINDOW_WIDTH = 850
WINDOW_HEIGHT = 600

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
    """Construye las vistas estáticas previstas para el Paso 1."""

    def __init__(self, root):
        self.root = root
        self.test_mode = tk.BooleanVar(value=False)
        self.quick_time = tk.StringVar(value="60 min")
        self.hours = tk.StringVar(value="0")
        self.minutes = tk.StringVar(value="2")
        self.warning_preview = False

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
            self.show_active_timer,
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

        tk.Label(
            panel,
            text=description,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=("Segoe UI Semibold", 18),
            takefocus=False,
        ).pack(pady=((22 if self.warning_preview else 35), 4))

        tk.Label(
            panel,
            text="00:00:45" if self.warning_preview else "01:00:00",
            bg=COLORS["panel"],
            fg=COLORS["warning"] if self.warning_preview else COLORS["text"],
            font=("Consolas", 68, "bold"),
            takefocus=False,
        ).pack(pady=(0, 5))

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
            mode_text = (
                "MODO DE PRUEBA — La PC no se apagará"
                if self.test_mode.get()
                else "Timer activo"
            )
            tk.Label(
                panel,
                text=mode_text,
                bg=COLORS["panel"],
                fg=COLORS["warning"] if self.test_mode.get() else COLORS["muted"],
                font=("Segoe UI Semibold", 11),
                takefocus=False,
            ).pack(pady=(0, 16))

        primary_controls = tk.Frame(panel, bg=COLORS["panel"])
        primary_controls.pack(pady=(0, 13))
        self._button(primary_controls, "Pausa", self._simulate_pause).pack(
            side="left", padx=7
        )
        self._button(
            primary_controls,
            "CANCELAR" if self.warning_preview else "Cancelar",
            self.show_configuration,
            kind="danger",
        ).pack(side="left", padx=7)

        add_controls = tk.Frame(panel, bg=COLORS["panel"])
        add_controls.pack(pady=(0, 12))
        self._button(add_controls, "+15 min", self._static_action, width=12).pack(
            side="left", padx=7
        )
        self._button(add_controls, "+30 min", self._static_action, width=12).pack(
            side="left", padx=7
        )

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

    def _toggle_warning_preview(self):
        self.warning_preview = not self.warning_preview
        self.show_active_timer()

    def _simulate_pause(self):
        """Paso 1: control visual sin modificar el tiempo mostrado."""

    def _static_action(self):
        """Paso 1: los botones de suma quedan visibles pero aún no actúan."""


def main():
    root = tk.Tk()
    PCNightTimerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

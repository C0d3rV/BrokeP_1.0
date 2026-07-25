import customtkinter as ctk

NAV_ITEMS = [
    ("Dashboard", "dashboard"),
    ("Data Entry", "data_entry"),
    ("Reports", "reports"),
]


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BrokeP")
        self.geometry("1200x760")
        self.minsize(1000, 640)

        self.session_state = {
            "trade_batch": [],
            "selected_client_id": None,
        }

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.current_screen = None
        self._show_screen("dashboard")

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        logo = ctk.CTkLabel(sidebar, text="BrokeP", font=ctk.CTkFont(size=20, weight="bold"))
        logo.pack(pady=(24, 30), padx=20, anchor="w")

        self.nav_buttons = {}
        for label, key in NAV_ITEMS:
            btn = ctk.CTkButton(
                sidebar, text=label, anchor="w", fg_color="transparent",
                text_color=("gray10", "gray90"), hover_color=("gray80", "gray25"),
                command=lambda k=key: self._show_screen(k)
            )
            btn.pack(fill="x", padx=12, pady=2)
            self.nav_buttons[key] = btn

    def _show_screen(self, screen_key: str):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        for key, btn in self.nav_buttons.items():
            btn.configure(fg_color=("gray75", "gray30") if key == screen_key else "transparent")

        builder = self._resolve_builder(screen_key)
        screen = builder(self.content_frame, self)
        screen.pack(fill="both", expand=True)
        self.current_screen = screen_key

    def _resolve_builder(self, screen_key: str):
        if screen_key == "dashboard":
            from app.ui.screens.dashboard_screen import build
        elif screen_key == "data_entry":
            from app.ui.screens.data_entry_screen import build
        elif screen_key == "reports":
            from app.ui.screens.report_screen import build
        else:
            raise ValueError(f"Unknown screen: {screen_key}")
        return build
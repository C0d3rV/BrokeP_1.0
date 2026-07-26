import customtkinter as ctk
import traceback
from app.ui.theme import font, configure_ttk_style, BG_APP, BG_SIDEBAR, PRIMARY

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
        self.configure(fg_color=BG_APP)

        configure_ttk_style()

        self.session_state = {
            "trade_batch": [],
            "selected_client_id": None,
        }

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self._screens = {}
        self.current_screen = None
        self._show_screen("dashboard")

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=BG_SIDEBAR)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text="BrokeP", font=font(22, "bold"), text_color="#FFFFFF").pack(
            pady=(24, 30), padx=20, anchor="w"
        )

        self.nav_buttons = {}
        for label, key in NAV_ITEMS:
            btn = ctk.CTkButton(
                sidebar, text=label, anchor="w", fg_color="transparent",
                text_color=("#C7CCDA", "#C7CCDA"), hover_color=("#2A2F3D", "#2A2F3D"),
                font=font(14), command=lambda k=key: self._show_screen(k)
            )
            btn.pack(fill="x", padx=12, pady=2)
            self.nav_buttons[key] = btn

    def _show_screen(self, screen_key: str):
        if screen_key == self.current_screen:
            return

        # Hide whatever is currently visible -- but only after we know the
        # new screen actually builds successfully (see below), so a broken
        # screen can never leave the content area blank with no way back.
        previous_screen = self.current_screen

        try:
            if screen_key not in self._screens:
                builder = self._resolve_builder(screen_key)
                screen = builder(self.content_frame, self)
                screen.grid(row=0, column=0, sticky="nsew")
                screen.grid_remove()  # start hidden, shown below alongside the swap
                self._screens[screen_key] = screen
            new_screen = self._screens[screen_key]

            if previous_screen is not None and previous_screen in self._screens:
                self._screens[previous_screen].grid_remove()

            new_screen.grid()
            if hasattr(new_screen, "on_show"):
                new_screen.on_show()

        except Exception:
            # Never leave the app in a stuck, blank state. Show the error
            # and keep navigation state consistent so every sidebar button
            # keeps working regardless of what just broke.
            traceback.print_exc()
            self._show_error_screen(screen_key)

        for key, btn in self.nav_buttons.items():
            btn.configure(fg_color=PRIMARY if key == screen_key else "transparent")

        self.current_screen = screen_key

    def _show_error_screen(self, screen_key):
        for widget in self.content_frame.winfo_children():
            widget.grid_remove()
        error_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        error_frame.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(
            error_frame, text=f"Couldn't load this screen.\nCheck the terminal for details.",
            font=font(14), text_color="#C0392B"
        ).pack(pady=40)
        self._screens[screen_key] = error_frame

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
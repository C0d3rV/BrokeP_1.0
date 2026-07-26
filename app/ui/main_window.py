import customtkinter as ctk
import traceback
from app.ui.theme import font, configure_ttk_style, BG_APP, BG_CARD, PRIMARY, PRIMARY_HOVER, TEXT_MUTED

NAV_ITEMS = [
    ("Home", "dashboard"),
    ("+ Data", "data_entry"),
    ("Reports", "reports"),
]

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BrokeP")
        self.geometry("1200x760")
        self.minsize(1000, 640)
        self.configure(fg_color=BG_APP)

        self.attributes("-alpha", 0.99) 
        self.after(100, lambda: self.attributes("-alpha", 1.0))

        configure_ttk_style()

        self.session_state = {
            "trade_batch": [],
            "selected_client_id": None,
        }

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_top_bar()

        # Dedicated content container with explicit background caching
        self.content_frame = ctk.CTkFrame(self, fg_color=BG_APP, corner_radius=0)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self._screens = {}
        self.current_screen = None
        
        # Initial load cached cleanly
        self.after(30, lambda: self._show_screen("dashboard"))

    def _build_top_bar(self):
        top_bar = ctk.CTkFrame(self, height=50, corner_radius=0, fg_color=BG_CARD)
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.grid_propagate(False)

        ctk.CTkLabel(
            top_bar, text="BrokeP", font=font(16, "bold"), text_color=("gray10", "gray95")
        ).pack(side="left", padx=(20, 10), pady=10)

        nav_frame = ctk.CTkFrame(top_bar, fg_color="transparent")
        nav_frame.pack(side="left", expand=True, fill="x", padx=(40, 10), pady=10)

        self.nav_buttons = {}
        for label, key in NAV_ITEMS:
            btn = ctk.CTkButton(
                nav_frame, text=label, font=font(12, "bold"), width=100, height=30,
                corner_radius=8, fg_color="transparent",
                text_color=("gray10", "gray95"), hover_color=("gray85", "gray25"),
                command=lambda k=key: self._show_screen(k))
            btn.pack(side="left", padx=6, pady=10)
            self.nav_buttons[key] = btn

    def _show_screen(self, screen_key: str):
        if screen_key == self.current_screen:
            return

        try:
            # 1. Lazy Initialization: Build and cache screen into memory only once
            if screen_key not in self._screens:
                builder = self._resolve_builder(screen_key)
                screen = builder(self.content_frame, self)
                # Stack all cached screens in the exact same grid cell layout slot
                screen.grid(row=0, column=0, sticky="nsew")
                self._screens[screen_key] = screen

            cached_screen = self._screens[screen_key]

            # 2. Instant Memory Switch: tkraise brings the cached frame to the top instantly without redraw flicker
            cached_screen.tkraise()

            if hasattr(cached_screen, "on_show"):
                cached_screen.on_show()

        except Exception:
            traceback.print_exc()
            self._show_error_screen(screen_key)

        # Update Navigation Button Highlighting State
        for key, btn in self.nav_buttons.items():
            if key == screen_key:
                btn.configure(fg_color=PRIMARY, text_color="white", hover_color=PRIMARY_HOVER)
            else:
                btn.configure(fg_color="transparent", text_color=("gray20", "gray90"),
                              hover_color=("gray85", "gray25"))

        self.current_screen = screen_key

    def _show_error_screen(self, screen_key):
        error_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        error_frame.grid(row=0, column=0, sticky="nsew")
        error_frame.tkraise()
        ctk.CTkLabel(
            error_frame, text="Couldn't load this screen.\nCheck the terminal for details.",
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
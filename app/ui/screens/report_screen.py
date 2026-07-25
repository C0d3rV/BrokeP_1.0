import customtkinter as ctk

from app.services import client_service, trade_service

SEGMENTS = ["All segments", "EQUITY", "FNO", "COMMODITY"]


class ReportScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.clients = []

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_filter_panel()
        self._build_results_panel()

        self._refresh_clients()
        self._apply_filters()

    def _build_filter_panel(self):
        panel = ctk.CTkFrame(self, width=260, corner_radius=12)
        panel.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        panel.grid_propagate(False)

        pad = {"padx": 20, "pady": (12, 0)}

        ctk.CTkLabel(panel, text="Client").pack(anchor="w", **pad)
        self.client_dropdown = ctk.CTkOptionMenu(panel, values=["All clients"])
        self.client_dropdown.pack(fill="x", padx=20)

        ctk.CTkLabel(panel, text="Segment").pack(anchor="w", **pad)
        self.segment_dropdown = ctk.CTkOptionMenu(panel, values=SEGMENTS)
        self.segment_dropdown.pack(fill="x", padx=20)

        ctk.CTkLabel(panel, text="Status").pack(anchor="w", **pad)
        self.status_dropdown = ctk.CTkOptionMenu(panel, values=["All", "OPEN", "CLOSED"])
        self.status_dropdown.pack(fill="x", padx=20)

        ctk.CTkButton(panel, text="Apply filters", command=self._apply_filters).pack(
            fill="x", padx=20, pady=20
        )

    def _build_results_panel(self):
        panel = ctk.CTkFrame(self, corner_radius=12)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(2, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        summary_row = ctk.CTkFrame(panel, fg_color="transparent")
        summary_row.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))

        self.summary_labels = {}
        for key, label in [("count", "Trades"), ("pnl", "Net P&L"), ("brokerage", "Brokerage")]:
            card = ctk.CTkFrame(summary_row, corner_radius=10)
            card.pack(side="left", fill="both", expand=True, padx=6)
            ctk.CTkLabel(card, text=label, text_color=("gray30", "gray70")).pack(anchor="w", padx=14, pady=(10, 2))
            val = ctk.CTkLabel(card, text="0", font=ctk.CTkFont(size=18, weight="bold"))
            val.pack(anchor="w", padx=14, pady=(0, 10))
            self.summary_labels[key] = val

        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=1, column=0, sticky="ew", padx=16, pady=(4, 4))
        for i, text in enumerate(["Client", "Symbol", "Qty", "Entry", "Exit", "Net P&L", "Status"]):
            ctk.CTkLabel(header, text=text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=i, padx=8, sticky="w")

        self.results_scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self.results_scroll.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 16))

    def _refresh_clients(self):
        self.clients = client_service.list_clients()
        names = ["All clients"] + [c.name for c in self.clients]
        self.client_dropdown.configure(values=names)
        self.client_dropdown.set(names[0])

    def _apply_filters(self):
        all_trades = trade_service.list_all_open_trades() + trade_service.list_all_closed_trades()

        client_filter = self.client_dropdown.get()
        segment_filter = self.segment_dropdown.get()
        status_filter = self.status_dropdown.get()

        filtered = all_trades
        if client_filter != "All clients":
            match = next((c for c in self.clients if c.name == client_filter), None)
            if match:
                filtered = [t for t in filtered if t.client_id == match.client_id]
        if segment_filter != "All segments":
            filtered = [t for t in filtered if t.segment == segment_filter]
        if status_filter != "All":
            filtered = [t for t in filtered if t.status == status_filter]

        self._render_results(filtered)

    def _client_name(self, client_id):
        match = next((c for c in self.clients if c.client_id == client_id), None)
        return match.name if match else str(client_id)

    def _render_results(self, trades):
        for w in self.results_scroll.winfo_children():
            w.destroy()

        total_pnl = sum(t.net_pl or 0 for t in trades)
        total_brokerage = sum((t.entry_brokerage or 0) + (t.exit_brokerage or 0) for t in trades)

        self.summary_labels["count"].configure(text=str(len(trades)))
        self.summary_labels["pnl"].configure(text=f"₹{total_pnl:,.2f}")
        self.summary_labels["brokerage"].configure(text=f"₹{total_brokerage:,.2f}")

        if not trades:
            ctk.CTkLabel(self.results_scroll, text="No trades match these filters.",
                         text_color=("gray40", "gray60")).pack(anchor="w", pady=8)
            return

        for t in trades:
            row = ctk.CTkFrame(self.results_scroll, fg_color="transparent")
            row.pack(fill="x", pady=2)
            color = "#1a7a4c" if t.status == "OPEN" else "#b23b3b"
            ctk.CTkLabel(row, text=self._client_name(t.client_id), width=100, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(row, text=t.symbol, width=80, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(row, text=str(t.quantity), width=60, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(row, text=t.entry_date, width=90, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(row, text=t.exit_date or "-", width=90, anchor="w").pack(side="left", padx=6)
            pnl_text = f"₹{t.net_pl:,.2f}" if t.net_pl is not None else "-"
            ctk.CTkLabel(row, text=pnl_text, width=90, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(row, text=t.status, text_color=color, width=70, anchor="w").pack(side="left", padx=6)


def build(parent, app) -> ctk.CTkFrame:
    return ReportScreen(parent, app)
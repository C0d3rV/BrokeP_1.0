import customtkinter as ctk

from app.services import client_service, trade_service
from app.ui.theme import font, PRIMARY, PRIMARY_HOVER, BG_CARD
from app.ui.async_utils import run_in_background
from app.ui.widgets.data_table import DataTable

SEGMENTS = ["All segments", "EQUITY", "FNO", "COMMODITY"]
COLUMNS = [
    ("client", "Client", 120), ("symbol", "Symbol", 90), ("qty", "Qty", 70),
    ("entry", "Entry", 100), ("exit", "Exit", 100), ("pnl", "Net P&L", 110), ("status", "Status", 90),
]


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
        self.on_show()

    def _build_filter_panel(self):
        panel = ctk.CTkFrame(self, width=260, corner_radius=14, fg_color=BG_CARD)
        panel.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        panel.grid_propagate(False)
        pad = {"padx": 20, "pady": (12, 0)}

        ctk.CTkLabel(panel, text="Client", font=font(13)).pack(anchor="w", **pad)
        self.client_dropdown = ctk.CTkOptionMenu(panel, values=["All clients"], font=font(13),
                                                    fg_color=PRIMARY, button_color=PRIMARY_HOVER)
        self.client_dropdown.pack(fill="x", padx=20)

        ctk.CTkLabel(panel, text="Segment", font=font(13)).pack(anchor="w", **pad)
        self.segment_dropdown = ctk.CTkOptionMenu(panel, values=SEGMENTS, font=font(13),
                                                     fg_color=PRIMARY, button_color=PRIMARY_HOVER)
        self.segment_dropdown.pack(fill="x", padx=20)

        ctk.CTkLabel(panel, text="Status", font=font(13)).pack(anchor="w", **pad)
        self.status_dropdown = ctk.CTkOptionMenu(panel, values=["All", "OPEN", "CLOSED"], font=font(13),
                                                    fg_color=PRIMARY, button_color=PRIMARY_HOVER)
        self.status_dropdown.pack(fill="x", padx=20)

        ctk.CTkButton(panel, text="Apply filters", font=font(13, "bold"), fg_color=PRIMARY,
                      hover_color=PRIMARY_HOVER, command=self._apply_filters).pack(fill="x", padx=20, pady=20)

    def _build_results_panel(self):
        panel = ctk.CTkFrame(self, corner_radius=14, fg_color=BG_CARD)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        summary_row = ctk.CTkFrame(panel, fg_color="transparent")
        summary_row.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        self.summary_labels = {}
        for key, label in [("count", "Trades"), ("pnl", "Net P&L"), ("brokerage", "Brokerage")]:
            card = ctk.CTkFrame(summary_row, corner_radius=10, fg_color=("#EDF1FC", "#242938"))
            card.pack(side="left", fill="both", expand=True, padx=6)
            ctk.CTkLabel(card, text=label, font=font(13), text_color=("gray30", "gray70")).pack(
                anchor="w", padx=14, pady=(10, 2)
            )
            val = ctk.CTkLabel(card, text="0", font=font(18, "bold"))
            val.pack(anchor="w", padx=14, pady=(0, 10))
            self.summary_labels[key] = val

        table_wrap = ctk.CTkFrame(panel, fg_color="transparent")
        table_wrap.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        table_wrap.grid_rowconfigure(0, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)
        self.table = DataTable(table_wrap, COLUMNS)
        self.table.grid(row=0, column=0, sticky="nsew")

    def on_show(self):
        run_in_background(self, work_fn=client_service.list_clients, on_done=self._apply_clients)

    def _apply_clients(self, result):
        if isinstance(result, Exception):
            return
        self.clients = result
        names = ["All clients"] + [c.name for c in self.clients]
        self.client_dropdown.configure(values=names)
        if self.client_dropdown.get() not in names:
            self.client_dropdown.set(names[0])
        self._apply_filters()

    def _apply_filters(self):
        run_in_background(
            self,
            work_fn=lambda: (trade_service.list_all_open_trades(), trade_service.list_all_closed_trades()),
            on_done=self._render_with_filters
        )

    def _render_with_filters(self, result):
        if isinstance(result, Exception):
            return
        open_trades, closed_trades = result
        all_trades = open_trades + closed_trades

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
        total_pnl = sum(t.net_pl or 0 for t in trades)
        total_brokerage = sum((t.entry_brokerage or 0) + (t.exit_brokerage or 0) for t in trades)

        self.summary_labels["count"].configure(text=str(len(trades)))
        self.summary_labels["pnl"].configure(text=f"₹{total_pnl:,.2f}")
        self.summary_labels["brokerage"].configure(text=f"₹{total_brokerage:,.2f}")

        rows = []
        for t in trades:
            pnl_text = f"₹{t.net_pl:,.2f}" if t.net_pl is not None else "-"
            rows.append((
                self._client_name(t.client_id), t.symbol, str(t.quantity),
                t.entry_date, t.exit_date or "-", pnl_text, t.status
            ))
        self.table.set_rows(rows)


def build(parent, app) -> ctk.CTkFrame:
    return ReportScreen(parent, app)
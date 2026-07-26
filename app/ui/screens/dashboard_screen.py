import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import date

from app.services import client_service, trade_service, mark_service, export_service
from app.ui.theme import font, PRIMARY, PRIMARY_HOVER, SUCCESS, SUCCESS_HOVER, BG_CARD, TEXT_MUTED
from app.ui.async_utils import run_in_background
from app.ui.widgets.data_table import DataTable

SNAPSHOT_COLUMNS = [
    ("symbol", "Symbol", 100), ("qty", "Qty", 60), ("entry_price", "Entry", 80),
    ("closing_price", "Closing", 80), ("unrealized", "Unrealized P&L", 110),
]


class DashboardScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.clients = []
        self.instrument_groups = {}
        self.price_entries = {}
        self.current_snapshot = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_right_panel()
        self.on_show()

    def _build_left_panel(self):
        panel = ctk.CTkFrame(self, corner_radius=14, fg_color=BG_CARD)
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        ctk.CTkLabel(header, text="Today's closing prices", font=font(16, "bold")).pack(anchor="w")
        ctk.CTkLabel(header, text="One price per instrument -- applies to every client holding it",
                     font=font(11), text_color=TEXT_MUTED).pack(anchor="w")

        self.price_scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self.price_scroll.grid(row=1, column=0, sticky="nsew", padx=16)

        ctk.CTkButton(panel, text="Save", font=font(13, "bold"), fg_color=SUCCESS,
                      hover_color=SUCCESS_HOVER, command=self._save_marks).grid(
            row=2, column=0, sticky="ew", padx=16, pady=16
        )

    def _refresh_instrument_list(self):
        for w in self.price_scroll.winfo_children():
            w.destroy()
        self.price_entries = {}

        open_trades = trade_service.list_all_open_trades()
        self.instrument_groups = mark_service.group_open_trades_by_instrument(open_trades)

        if not self.instrument_groups:
            ctk.CTkLabel(self.price_scroll, text="No open positions to mark.",
                         font=font(12), text_color=TEXT_MUTED).pack(anchor="w", pady=8)
            return

        for (symbol, expiry), trades in sorted(self.instrument_groups.items()):
            row = ctk.CTkFrame(self.price_scroll, fg_color="transparent")
            row.pack(fill="x", pady=4)
            label_text = f"{symbol}  (exp {expiry})" if expiry else symbol
            ctk.CTkLabel(row, text=label_text, font=font(13), width=180, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(row, placeholder_text="Closing price", font=font(13), width=120)
            entry.pack(side="left", padx=(8, 0))
            self.price_entries[(symbol, expiry)] = entry

    def _save_marks(self):
        today = date.today().isoformat()
        errors, saved_count = [], 0

        for key, entry in self.price_entries.items():
            text = entry.get().strip()
            if not text:
                continue
            try:
                price = float(text)
            except ValueError:
                errors.append(f"{key[0]}: invalid price")
                continue

            for trade in self.instrument_groups[key]:
                try:
                    mark_service.record_daily_mark(trade.trade_id, today, price)
                    saved_count += 1
                except ValueError as e:
                    errors.append(f"{key[0]} (trade {trade.trade_id}): {e}")

        self._refresh_client_snapshot()

        if errors:
            messagebox.showerror("Some marks failed", "\n".join(errors))
        else:
            messagebox.showinfo("Marks saved", f"Updated {saved_count} position(s) for {today}.")

    def _build_right_panel(self):
        panel = ctk.CTkFrame(self, corner_radius=14, fg_color=BG_CARD)
        panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        panel.grid_rowconfigure(2, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(panel, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        ctk.CTkLabel(top, text="Client snapshot", font=font(16, "bold")).pack(anchor="w")

        self.client_dropdown = ctk.CTkOptionMenu(
            panel, values=["Loading..."], font=font(13), fg_color=PRIMARY,
            button_color=PRIMARY_HOVER, command=lambda _v: self._refresh_client_snapshot()
        )
        self.client_dropdown.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))

        table_wrap = ctk.CTkFrame(panel, fg_color="transparent")
        table_wrap.grid(row=2, column=0, sticky="nsew", padx=16)
        table_wrap.grid_rowconfigure(0, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)
        self.snapshot_table = DataTable(table_wrap, SNAPSHOT_COLUMNS)
        self.snapshot_table.grid(row=0, column=0, sticky="nsew")

        export_row = ctk.CTkFrame(panel, fg_color="transparent")
        export_row.grid(row=3, column=0, sticky="ew", padx=16, pady=16)
        ctk.CTkButton(export_row, text="Export PDF", font=font(12), fg_color="#B7302B",
                      hover_color="#93261F", command=self._export_pdf).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(export_row, text="Export Excel", font=font(12), fg_color="#1D6F42",
                      hover_color="#155531", command=self._export_excel).pack(side="left", fill="x", expand=True, padx=(6, 0))

    def on_show(self):
        self._refresh_instrument_list()
        run_in_background(self, work_fn=client_service.list_clients, on_done=self._apply_clients)

    def _apply_clients(self, result):
        if isinstance(result, Exception):
            return
        self.clients = result
        names = [c.name for c in self.clients] or ["No clients yet"]
        self.client_dropdown.configure(values=names)
        self.client_dropdown.set(names[0])
        self._refresh_client_snapshot()

    def _selected_client(self):
        name = self.client_dropdown.get()
        return next((c for c in self.clients if c.name == name), None)

    def _refresh_client_snapshot(self):
        client = self._selected_client()
        if client is None:
            self.snapshot_table.clear()
            self.current_snapshot = []
            return

        today = date.today().isoformat()
        open_trades = trade_service.get_open_trades_for_client(client.client_id)
        pairs = [(t, mark_service.get_mark_for_trade(t.trade_id, today)) for t in open_trades]
        self.current_snapshot = pairs

        rows = []
        for t, m in pairs:
            closing = f"{m.closing_price:,.2f}" if m else "-"
            unrealized = f"{m.unrealized_net_pl:,.2f}" if m else "-"
            rows.append((t.symbol, str(t.quantity), f"{t.entry_price:,.2f}", closing, unrealized))
        self.snapshot_table.set_rows(rows)

    def _export_pdf(self):
        client = self._selected_client()
        if client is None or not self.current_snapshot:
            messagebox.showinfo("Nothing to export", "No open positions for this client.")
            return
        default_name = export_service.generate_filename(client.name, "DailySnapshot", "pdf")
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF file", "*.pdf")],
                                             initialfile=default_name)
        if not path:
            return
        try:
            export_service.export_daily_snapshot_to_pdf(self.current_snapshot, client.name, path)
            messagebox.showinfo("Exported", f"Saved to {path}")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))

    def _export_excel(self):
        client = self._selected_client()
        if client is None or not self.current_snapshot:
            messagebox.showinfo("Nothing to export", "No open positions for this client.")
            return
        default_name = export_service.generate_filename(client.name, "DailySnapshot", "xlsx")
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel file", "*.xlsx")],
                                             initialfile=default_name)
        if not path:
            return
        try:
            export_service.export_daily_snapshot_to_excel(self.current_snapshot, client.name, path)
            messagebox.showinfo("Exported", f"Saved to {path}")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))


def build(parent, app) -> ctk.CTkFrame:
    return DashboardScreen(parent, app)
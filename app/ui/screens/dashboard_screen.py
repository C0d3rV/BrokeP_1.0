import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime, date
import os

from app.services import client_service, trade_service, mark_service, export_service
from app.ui.theme import font, PRIMARY, PRIMARY_HOVER, SUCCESS, SUCCESS_HOVER, BG_CARD, TEXT_MUTED
from app.ui.async_utils import run_in_background
from app.ui.widgets.data_table import DataTable
from app.ui.widgets.date_picker import make_date_picker

SNAPSHOT_COLUMNS = [
    ("symbol", "Symbol", 120), ("qty", "Qty", 80), ("entry_price", "Avg Entry", 100),
    ("closing_price", "Closing Price", 100), ("unrealized", "Unrealized P&L", 120),
]

class DashboardScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.clients = []
        self.instrument_groups = {}
        self.price_entries = {}
        self.current_snapshot = []

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_left_panel()
        self._build_right_panel()
        self.on_show()

    def _build_left_panel(self):
        panel = ctk.CTkFrame(self, width=280, corner_radius=14, fg_color=BG_CARD)
        panel.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        panel.grid_propagate(False)
        panel.grid_rowconfigure(2, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        ctk.CTkLabel(header, text="Today's Closing Prices", font=font(16, "bold")).pack(anchor="w")
        ctk.CTkLabel(header, text="Updates all clients holding these assets", font=font(11), text_color=TEXT_MUTED).pack(anchor="w")

        self.status_banner = ctk.CTkLabel(panel, text="", font=font(12, "bold"))
        
        self.price_scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self.price_scroll.grid(row=2, column=0, sticky="nsew", padx=16, pady=5)

        self.btn_save_marks = ctk.CTkButton(panel, text="Save", font=font(13, "bold"), fg_color=SUCCESS,
                      hover_color=SUCCESS_HOVER, width=140, command=self._save_marks)
        self.btn_save_marks.grid(row=3, column=0, pady=20)

    def _selected_date(self) -> str:
        """Returns the ISO date selected in the dashboard header."""
        if hasattr(self, "date_picker"):
            return self.date_picker.get().strip()
        return date.today().isoformat()

    def _refresh_instrument_list(self):
        for w in self.price_scroll.winfo_children():
            w.destroy()
        self.price_entries = {}

        open_trades = trade_service.list_all_open_trades()
        self.instrument_groups = mark_service.group_open_trades_by_instrument(open_trades)

        if not self.instrument_groups:
            ctk.CTkLabel(self.price_scroll, text="No open positions.", font=font(12), text_color=TEXT_MUTED).pack(anchor="w", pady=8)
            self.status_banner.grid_remove()
            self.btn_save_marks.configure(state="disabled")
            return

        target_date = self._selected_date()
        all_updated = True

        for (symbol, expiry), trades in sorted(self.instrument_groups.items()):
            row = ctk.CTkFrame(self.price_scroll, fg_color="transparent")
            row.pack(fill="x", pady=6)
            label_text = f"{symbol} (exp {expiry})" if expiry else symbol
            
            ctk.CTkLabel(row, text=label_text, font=font(13, "bold"), anchor="w").pack(side="top", fill="x", padx=4)
            entry = ctk.CTkEntry(row, placeholder_text="Closing price", font=font(13))
            entry.pack(side="top", fill="x", padx=4, pady=(4, 0))
            
            mark_record = mark_service.get_mark_for_trade(trades[0].trade_id, target_date)
            if mark_record:
                price_val = getattr(mark_record, 'closing_price', None)
                if price_val is not None:
                    entry.insert(0, f"{price_val:.2f}")
            else:
                all_updated = False
                
            self.price_entries[(symbol, expiry)] = entry

        if all_updated and self.instrument_groups:
            self.status_banner.configure(text=f"✅ Prices updated for {target_date}", text_color=SUCCESS)
            self.status_banner.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 5))
            self.btn_save_marks.configure(state="normal")
        else:
            self.status_banner.grid_remove()
            self.btn_save_marks.configure(state="normal")

    def _save_marks(self):
        target_date = self._selected_date()
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
                    mark_service.record_daily_mark(trade.trade_id, target_date, price)
                    saved_count += 1
                except Exception as e:
                    errors.append(f"{key[0]}: {e}")

        self._refresh_instrument_list()
        self._refresh_client_snapshot()
        
        if errors:
            messagebox.showerror("Some marks failed", "\n".join(errors))
        elif saved_count > 0:
            messagebox.showinfo("Marks saved", f"Updated {saved_count} position(s) for {target_date}.")

    def _build_right_panel(self):
        panel = ctk.CTkFrame(self, corner_radius=14, fg_color=BG_CARD)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(2, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(panel, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        
        ctk.CTkLabel(top, text="Dashboard", font=font(16, "bold")).pack(side="left")

        # Date Selector Frame (Allows viewing historical statements)
        date_frame = ctk.CTkFrame(top, fg_color="transparent")
        date_frame.pack(side="left", padx=20)
        ctk.CTkLabel(date_frame, text="Statement Date:", font=font(12), text_color=TEXT_MUTED).pack(side="left", padx=(0, 6))
        self.date_picker = make_date_picker(date_frame, command=lambda e: self._on_date_change())
        self.date_picker.pack(side="left")

        select_frame = ctk.CTkFrame(top, fg_color="transparent")
        select_frame.pack(side="right")
        ctk.CTkLabel(select_frame, text="View:", font=font(13), text_color=TEXT_MUTED).pack(side="left", padx=(0, 10))
        self.client_dropdown = ctk.CTkOptionMenu(
            select_frame, values=["Loading..."], font=font(13), fg_color=PRIMARY,
            button_color=PRIMARY_HOVER, command=lambda _v: self._refresh_client_snapshot()
        )
        self.client_dropdown.pack(side="left")

        summary_row = ctk.CTkFrame(panel, fg_color="transparent")
        summary_row.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.dash_labels = {}
        for key, label in [("positions", "Open Positions"), ("exposure", "Total Invested"), ("unrealized", "Unrealized P&L")]:
            card = ctk.CTkFrame(summary_row, corner_radius=10, fg_color=("#EDF1FC", "#242938"))
            card.pack(side="left", fill="both", expand=True, padx=6)
            ctk.CTkLabel(card, text=label, font=font(13), text_color=("gray30", "gray70")).pack(anchor="w", padx=14, pady=(10, 2))
            val = ctk.CTkLabel(card, text="0", font=font(20, "bold"))
            val.pack(anchor="w", padx=14, pady=(0, 10))
            self.dash_labels[key] = val

        table_wrap = ctk.CTkFrame(panel, fg_color="transparent")
        table_wrap.grid(row=2, column=0, sticky="nsew", padx=16)
        table_wrap.grid_rowconfigure(0, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)
        self.snapshot_table = DataTable(table_wrap, SNAPSHOT_COLUMNS)
        self.snapshot_table.grid(row=0, column=0, sticky="nsew")

        export_row = ctk.CTkFrame(panel, fg_color="transparent")
        export_row.grid(row=3, column=0, sticky="e", padx=16, pady=16)
        ctk.CTkButton(export_row, text="Export PDF", font=font(12), fg_color="#B7302B", hover_color="#93261F", width=120, command=self._export_pdf).pack(side="right", padx=(10, 0))
        ctk.CTkButton(export_row, text="Export Excel", font=font(12), fg_color="#1D6F42", hover_color="#155531", width=120, command=self._export_excel).pack(side="right")

    def _on_date_change(self):
        self._refresh_instrument_list()
        self._refresh_client_snapshot()

    def on_show(self):
        self._refresh_instrument_list()
        run_in_background(self, work_fn=client_service.list_clients, on_done=self._apply_clients)

    def _apply_clients(self, result):
        if isinstance(result, Exception): return
        self.clients = result
        names = ["All clients"] + [c.name for c in self.clients]
        self.client_dropdown.configure(values=names)
        self.client_dropdown.set(names[0])
        self._refresh_client_snapshot()

    def _selected_client(self):
        name = self.client_dropdown.get()
        if name == "All clients": return None
        return next((c for c in self.clients if c.name == name), None)

    def _refresh_client_snapshot(self):
        client = self._selected_client()
        target_date = self._selected_date()
        
        if client:
            open_trades = trade_service.get_open_trades_for_client(client.client_id)
        else:
            open_trades = trade_service.list_all_open_trades()

        pairs = [(t, mark_service.get_mark_for_trade(t.trade_id, target_date)) for t in open_trades]
        self.current_snapshot = pairs

        total_exposure = sum((t.entry_price * t.quantity) for t in open_trades)
        total_unrealized = sum((getattr(m, 'unrealized_net_pl', 0) or 0) for t, m in pairs if m)

        self.dash_labels["positions"].configure(text=str(len(open_trades)))
        self.dash_labels["exposure"].configure(text=f"₹{total_exposure:,.2f}")
        pnl_color = "#12805C" if total_unrealized >= 0 else "#C0392B"
        self.dash_labels["unrealized"].configure(text=f"₹{total_unrealized:,.2f}", text_color=pnl_color)

        rows = []
        for t, m in pairs:
            closing = f"{getattr(m, 'closing_price', 0):,.2f}" if m else "-"
            unrealized = f"{getattr(m, 'unrealized_net_pl', 0):,.2f}" if m else "-"
            status_tag = "profit" if m and getattr(m, 'unrealized_net_pl', -1) >= 0 else "loss" if m else None
            rows.append((t.symbol, str(t.quantity), f"{t.entry_price:,.2f}", closing, unrealized, status_tag))
        self.snapshot_table.set_rows(rows)

    def _export_pdf(self):
        client = self._selected_client()
        if not client:
            messagebox.showwarning("Export Failed", "Please select a specific client from the dropdown to generate their financial ledger.")
            return
            
        if not self.current_snapshot:
            messagebox.showinfo("Nothing to export", "No open positions to export.")
            return
            
        default_name = export_service.generate_filename(client.name, "DailySnapshot", "pdf")
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF file", "*.pdf")], initialfile=default_name)
        if not path: return
        try:
            export_service.export_daily_snapshot_to_pdf(self.current_snapshot, client, path)
            messagebox.showinfo("Exported", f"Saved to {path}")
        except Exception as e: messagebox.showerror("Export failed", str(e))

    def _export_excel(self):
        client = self._selected_client()
        if not client:
            messagebox.showwarning("Export Failed", "Please select a specific client from the dropdown to generate their financial ledger.")
            return
            
        if not self.current_snapshot:
            messagebox.showinfo("Nothing to export", "No open positions to export.")
            return
            
        default_name = export_service.generate_filename(client.name, "DailySnapshot", "xlsx")
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel file", "*.xlsx")], initialfile=default_name)
        if not path: return
        try:
            export_service.export_daily_snapshot_to_excel(self.current_snapshot, client, path)
            messagebox.showinfo("Exported", f"Saved to {path}")
        except Exception as e: messagebox.showerror("Export failed", str(e))

def build(parent, app) -> ctk.CTkFrame:
    return DashboardScreen(parent, app)
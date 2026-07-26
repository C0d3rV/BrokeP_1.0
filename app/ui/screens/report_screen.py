from os import path

import customtkinter as ctk
from tkinter import filedialog, messagebox

from app.services import client_service, agent_service, trade_service, export_service, backup_service
from app.ui.theme import font, PRIMARY, PRIMARY_HOVER, SUCCESS, SUCCESS_HOVER, BG_CARD, TEXT_MUTED
from app.ui.async_utils import run_in_background
from app.ui.widgets.data_table import DataTable

SEGMENTS = ["All segments", "EQUITY", "FNO", "COMMODITY"]

COLUMNS = [
    ("client", "Client", 100), ("agent", "Agent", 90), ("segment", "Segment", 85),
    ("symbol", "Symbol", 80), ("qty", "Qty", 55),
    ("entry_date", "Entry Dt", 85), ("entry_price", "Entry Rate", 85),
    ("exit_date", "Exit Dt", 85), ("exit_price", "Exit Rate", 85),
    ("brokerage", "Brokerage", 85), ("svc_fee", "Svc Fee", 75),
    ("gross_pl", "Gross P&L", 85), ("net_pl", "Net P&L", 85), ("status", "Status", 70),
]


class ReportScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.clients = []
        self.agents = []
        self.current_trades = []

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
                      hover_color=PRIMARY_HOVER, command=self._apply_filters).pack(fill="x", padx=20, pady=(20, 10))

        ctk.CTkFrame(panel, height=1, fg_color=("gray80", "gray30")).pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(panel, text="Export & backup", font=font(13, "bold")).pack(anchor="w", padx=20)

        ctk.CTkLabel(panel, text="Copy type", font=font(12), text_color=TEXT_MUTED).pack(
            anchor="w", padx=20, pady=(10, 2)
        )
        self.copy_type_selector = ctk.CTkSegmentedButton(
            panel, values=["Client copy", "Broker copy"], font=font(12),
            selected_color=PRIMARY, selected_hover_color=PRIMARY_HOVER
        )
        self.copy_type_selector.set("Client copy")
        self.copy_type_selector.pack(fill="x", padx=20, pady=(0, 4))
        ctk.CTkLabel(
            panel, text="Broker copy hides service fee and\nexcludes it from Net P&L.",
            font=font(10), text_color=TEXT_MUTED, justify="left"
        ).pack(anchor="w", padx=20, pady=(0, 10))

        ctk.CTkButton(panel, text="Export to Excel", font=font(12), fg_color="#1D6F42",
                      hover_color="#155531", command=self._export_excel).pack(fill="x", padx=20, pady=(0, 6))
        ctk.CTkButton(panel, text="Export to PDF", font=font(12), fg_color="#B7302B",
                      hover_color="#93261F", command=self._export_pdf).pack(fill="x", padx=20)

        self.backup_status_label = ctk.CTkLabel(panel, text="", font=font(10), text_color=TEXT_MUTED)
        self.backup_status_label.pack(anchor="w", padx=20, pady=(14, 2))
        ctk.CTkButton(panel, text="Backup now", font=font(12), fg_color=SUCCESS,
                      hover_color=SUCCESS_HOVER, command=self._backup_now).pack(fill="x", padx=20, pady=(0, 20))

        self._refresh_backup_label()

    def _build_results_panel(self):
        panel = ctk.CTkFrame(self, corner_radius=14, fg_color=BG_CARD)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        summary_row = ctk.CTkFrame(panel, fg_color="transparent")
        summary_row.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        self.summary_labels = {}
        for key, label in [("count", "Trades"), ("pnl", "Net P&L"), ("brokerage", "Brokerage"), ("fees", "Service fees")]:
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
        run_in_background(self, work_fn=self._fetch_reference_data, on_done=self._apply_reference_data)
        self._refresh_backup_label()

    def _fetch_reference_data(self):
        return client_service.list_clients(), agent_service.list_agents()

    def _apply_reference_data(self, result):
        if isinstance(result, Exception):
            return
        self.clients, self.agents = result
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

    def _agent_name(self, agent_id):
        match = next((a for a in self.agents if a.agent_id == agent_id), None)
        return match.name if match else str(agent_id)

    def _render_results(self, trades):
        self.current_trades = trades

        total_pnl = sum(t.net_pl or 0 for t in trades)
        total_brokerage = sum((t.entry_brokerage or 0) + (t.exit_brokerage or 0) for t in trades)
        total_fees = sum((t.entry_service_fee or 0) + (t.exit_service_fee or 0) for t in trades)

        self.summary_labels["count"].configure(text=str(len(trades)))
        self.summary_labels["pnl"].configure(text=f"₹{total_pnl:,.2f}")
        self.summary_labels["brokerage"].configure(text=f"₹{total_brokerage:,.2f}")
        self.summary_labels["fees"].configure(text=f"₹{total_fees:,.2f}")

        rows = []
        for t in trades:
            brokerage_total = (t.entry_brokerage or 0) + (t.exit_brokerage or 0)
            fee_total = (t.entry_service_fee or 0) + (t.exit_service_fee or 0)
            gross_text = f"{t.gross_pl:,.2f}" if t.gross_pl is not None else "-"
            net_text = f"{t.net_pl:,.2f}" if t.net_pl is not None else "-"
            rows.append((
                self._client_name(t.client_id), self._agent_name(t.agent_id), t.segment,
                t.symbol, str(t.quantity),
                t.entry_date, f"{t.entry_price:,.2f}",
                t.exit_date or "-", f"{t.exit_price:,.2f}" if t.exit_price is not None else "-",
                f"{brokerage_total:,.2f}", f"{fee_total:,.2f}",
                gross_text, net_text, t.status
            ))
        self.table.set_rows(rows)

    def _copy_type(self) -> str:
        return "client" if self.copy_type_selector.get() == "Client copy" else "broker"

    def _default_export_name(self, ext: str) -> str:
        client_name = self.client_dropdown.get()  # "All clients" or a specific name
        report_type = "ClientCopy" if self._copy_type() == "client" else "BrokerCopy"
        return export_service.generate_filename(client_name, report_type, ext)

    def _export_excel(self):
        if not self.current_trades:
            messagebox.showinfo("Nothing to export", "No trades match the current filters.")
            return 
        path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                         filetypes=[("Excel file", "*.xlsx")],
                                         initialfile=self._default_export_name("xlsx"))
        if not path:
            return
        try:
            export_service.export_trades_to_excel(
                self.current_trades, self._client_name, self._agent_name, path, self._copy_type()
            ) 
            messagebox.showinfo("Exported", f"Saved to {path}")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))

    def _export_pdf(self):
        if not self.current_trades:
            messagebox.showinfo("Nothing to export", "No trades match the current filters.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                         filetypes=[("PDF file", "*.pdf")],
                                         initialfile=self._default_export_name("pdf"))
        if not path:
            return
        try:
            export_service.export_trades_to_pdf(
                self.current_trades, self._client_name, self._agent_name, path, self._copy_type()
            )
            messagebox.showinfo("Exported", f"Saved to {path}")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))

    def _refresh_backup_label(self):
        last = backup_service.last_backup_time()
        text = f"Last backup: {last}" if last else "No backups yet"
        self.backup_status_label.configure(text=text)

    def _backup_now(self):
        try:
            path = backup_service.backup_now()
            self._refresh_backup_label()
            messagebox.showinfo("Backup complete", f"Saved to {path}")
        except Exception as e:
            messagebox.showerror("Backup failed", str(e))


def build(parent, app) -> ctk.CTkFrame:
    return ReportScreen(parent, app)
import customtkinter as ctk
from tkinter import messagebox

from app.services import client_service, agent_service, trade_service, cash_service
from app.domain.calculations.pnl import gross_value

SEGMENTS = ["EQUITY", "FNO", "COMMODITY"]
TXN_TYPES = ["BUY", "SELL", "DEPOSIT", "WITHDRAWAL"]


class DataEntryScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.batch = app.session_state.setdefault("trade_batch", [])

        self.clients = []
        self.agents = []
        self.open_trades_for_client = []

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_form_panel()
        self._build_batch_panel()

        self._refresh_clients()
        self._refresh_agents()
        self._on_txn_type_change("BUY")
        self._refresh_batch_table()

    # ---------- LEFT: FORM ----------

    def _build_form_panel(self):
        panel = ctk.CTkFrame(self, width=320, corner_radius=12)
        panel.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        panel.grid_propagate(False)

        pad = {"padx": 20, "pady": (12, 0)}

        ctk.CTkLabel(panel, text="Client").pack(anchor="w", **pad)
        row = ctk.CTkFrame(panel, fg_color="transparent")
        row.pack(fill="x", padx=20)
        self.client_dropdown = ctk.CTkOptionMenu(row, values=["Loading..."], command=self._on_client_change)
        self.client_dropdown.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row, text="+ New", width=60, command=self._open_new_client_modal).pack(side="left", padx=(6, 0))

        ctk.CTkLabel(panel, text="Agent / Broker").pack(anchor="w", **pad)
        row2 = ctk.CTkFrame(panel, fg_color="transparent")
        row2.pack(fill="x", padx=20)
        self.agent_dropdown = ctk.CTkOptionMenu(row2, values=["Loading..."])
        self.agent_dropdown.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row2, text="+ New", width=60, command=self._open_new_agent_modal).pack(side="left", padx=(6, 0))

        seg_row = ctk.CTkFrame(panel, fg_color="transparent")
        seg_row.pack(fill="x", padx=20, pady=(12, 0))
        seg_col = ctk.CTkFrame(seg_row, fg_color="transparent")
        seg_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(seg_col, text="Segment").pack(anchor="w")
        self.segment_dropdown = ctk.CTkOptionMenu(seg_col, values=SEGMENTS)
        self.segment_dropdown.pack(fill="x")

        type_col = ctk.CTkFrame(seg_row, fg_color="transparent")
        type_col.pack(side="left", fill="x", expand=True, padx=(10, 0))
        ctk.CTkLabel(type_col, text="Txn type").pack(anchor="w")
        self.txn_type_dropdown = ctk.CTkOptionMenu(type_col, values=TXN_TYPES, command=self._on_txn_type_change)
        self.txn_type_dropdown.pack(fill="x")

        self.dynamic_area = ctk.CTkFrame(panel, fg_color="transparent")
        self.dynamic_area.pack(fill="x", padx=20, pady=(12, 0))

        self.gross_value_label = ctk.CTkLabel(
            panel, text="Gross value\n₹0", justify="left",
            fg_color=("gray85", "gray20"), corner_radius=8
        )
        self.gross_value_label.pack(fill="x", padx=20, pady=(16, 0), ipady=8)

        ctk.CTkButton(panel, text="+ Add to batch", command=self._add_to_batch).pack(
            fill="x", padx=20, pady=(16, 20)
        )

    def _on_txn_type_change(self, txn_type):
        for w in self.dynamic_area.winfo_children():
            w.destroy()

        if txn_type == "BUY":
            self._build_buy_fields()
        elif txn_type == "SELL":
            self._build_sell_fields()
        else:
            self._build_cash_fields()

    def _build_buy_fields(self):
        self.symbol_entry = ctk.CTkEntry(self.dynamic_area, placeholder_text="Symbol")
        self.symbol_entry.pack(fill="x", pady=(0, 8))

        qp_row = ctk.CTkFrame(self.dynamic_area, fg_color="transparent")
        qp_row.pack(fill="x", pady=(0, 8))
        self.quantity_entry = ctk.CTkEntry(qp_row, placeholder_text="Quantity")
        self.quantity_entry.pack(side="left", fill="x", expand=True)
        self.price_entry = ctk.CTkEntry(qp_row, placeholder_text="Price")
        self.price_entry.pack(side="left", fill="x", expand=True, padx=(6, 0))

        for e in (self.quantity_entry, self.price_entry):
            e.bind("<KeyRelease>", lambda _e: self._update_gross_preview())

        self.date_entry = ctk.CTkEntry(self.dynamic_area, placeholder_text="Entry date (YYYY-MM-DD)")
        self.date_entry.pack(fill="x", pady=(0, 8))

        self.manual_fee_entry = ctk.CTkEntry(self.dynamic_area, placeholder_text="Manual fee (optional)")
        self.manual_fee_entry.pack(fill="x", pady=(0, 8))

        self.remarks_entry = ctk.CTkEntry(self.dynamic_area, placeholder_text="Remarks")
        self.remarks_entry.pack(fill="x")

        self._update_gross_preview()

    def _build_sell_fields(self):
        ctk.CTkLabel(self.dynamic_area, text="Open trade to close").pack(anchor="w")
        self.open_trade_dropdown = ctk.CTkOptionMenu(self.dynamic_area, values=["Select client first"])
        self.open_trade_dropdown.pack(fill="x", pady=(0, 8))
        self._refresh_open_trades()

        self.exit_price_entry = ctk.CTkEntry(self.dynamic_area, placeholder_text="Exit price")
        self.exit_price_entry.pack(fill="x", pady=(0, 8))
        self.exit_price_entry.bind("<KeyRelease>", lambda _e: self._update_gross_preview())

        self.exit_date_entry = ctk.CTkEntry(self.dynamic_area, placeholder_text="Exit date (YYYY-MM-DD)")
        self.exit_date_entry.pack(fill="x", pady=(0, 8))

        self.service_fee_entry = ctk.CTkEntry(self.dynamic_area, placeholder_text="Service fee (optional)")
        self.service_fee_entry.pack(fill="x", pady=(0, 8))

        self.sell_manual_fee_entry = ctk.CTkEntry(self.dynamic_area, placeholder_text="Manual brokerage (optional)")
        self.sell_manual_fee_entry.pack(fill="x")

        self._update_gross_preview()

    def _build_cash_fields(self):
        self.cash_amount_entry = ctk.CTkEntry(self.dynamic_area, placeholder_text="Amount")
        self.cash_amount_entry.pack(fill="x", pady=(0, 8))
        self.cash_amount_entry.bind("<KeyRelease>", lambda _e: self._update_gross_preview())

        self.cash_date_entry = ctk.CTkEntry(self.dynamic_area, placeholder_text="Date (YYYY-MM-DD)")
        self.cash_date_entry.pack(fill="x", pady=(0, 8))

        self.cash_remarks_entry = ctk.CTkEntry(self.dynamic_area, placeholder_text="Remarks")
        self.cash_remarks_entry.pack(fill="x")

        self._update_gross_preview()

    def _update_gross_preview(self):
        txn_type = self.txn_type_dropdown.get()
        try:
            if txn_type == "BUY":
                qty = float(self.quantity_entry.get() or 0)
                price = float(self.price_entry.get() or 0)
                gv = gross_value(price, qty)
            elif txn_type == "SELL":
                qty = self._selected_open_trade_qty()
                price = float(self.exit_price_entry.get() or 0)
                gv = gross_value(price, qty)
            else:
                gv = float(self.cash_amount_entry.get() or 0)
        except ValueError:
            gv = 0
        self.gross_value_label.configure(text=f"Gross value\n₹{gv:,.2f}")

    def _refresh_clients(self):
        self.clients = client_service.list_clients()
        names = [c.name for c in self.clients] or ["No clients yet"]
        self.client_dropdown.configure(values=names)
        self.client_dropdown.set(names[0])
        self._on_client_change(names[0])

    def _refresh_agents(self):
        self.agents = agent_service.list_agents()
        names = [a.name for a in self.agents] or ["No agents yet"]
        self.agent_dropdown.configure(values=names)
        self.agent_dropdown.set(names[0])

    def _on_client_change(self, _selected_name):
        if self.txn_type_dropdown.get() == "SELL":
            self._refresh_open_trades()

    def _selected_client_id(self):
        name = self.client_dropdown.get()
        match = next((c for c in self.clients if c.name == name), None)
        return match.client_id if match else None

    def _selected_agent_id(self):
        name = self.agent_dropdown.get()
        match = next((a for a in self.agents if a.name == name), None)
        return match.agent_id if match else None

    def _refresh_open_trades(self):
        client_id = self._selected_client_id()
        self.open_trades_for_client = (
            trade_service.get_open_trades_for_client(client_id) if client_id else []
        )
        labels = [f"{t.symbol}  ({t.quantity} @ {t.entry_price})" for t in self.open_trades_for_client]
        if not labels:
            labels = ["No open trades"]
        self.open_trade_dropdown.configure(values=labels)
        self.open_trade_dropdown.set(labels[0])

    def _selected_open_trade(self):
        label = self.open_trade_dropdown.get()
        idx = None
        for i, t in enumerate(self.open_trades_for_client):
            if f"{t.symbol}  ({t.quantity} @ {t.entry_price})" == label:
                idx = i
                break
        return self.open_trades_for_client[idx] if idx is not None else None

    def _selected_open_trade_qty(self):
        t = self._selected_open_trade()
        return t.quantity if t else 0

    def _open_new_client_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("New client")
        modal.geometry("300x150")
        ctk.CTkLabel(modal, text="Client name").pack(pady=(16, 4))
        name_entry = ctk.CTkEntry(modal)
        name_entry.pack(padx=20, fill="x")

        def save():
            try:
                client_service.create_client(name_entry.get())
                modal.destroy()
                self._refresh_clients()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(modal, text="Save", command=save).pack(pady=16)

    def _open_new_agent_modal(self):
        modal = ctk.CTkToplevel(self)
        modal.title("New agent")
        modal.geometry("300x200")
        ctk.CTkLabel(modal, text="Agent name").pack(pady=(16, 4))
        name_entry = ctk.CTkEntry(modal)
        name_entry.pack(padx=20, fill="x")
        ctk.CTkLabel(modal, text="Brokerage rate (%)").pack(pady=(12, 4))
        rate_entry = ctk.CTkEntry(modal)
        rate_entry.pack(padx=20, fill="x")

        def save():
            try:
                rate = float(rate_entry.get())
                agent_service.create_agent(name_entry.get(), rate)
                modal.destroy()
                self._refresh_agents()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(modal, text="Save", command=save).pack(pady=16)

    def _build_batch_panel(self):
        panel = ctk.CTkFrame(self, corner_radius=12)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        for i, text in enumerate(["Client", "Type", "Segment/Symbol", "Qty", "Price", "Gross", ""]):
            ctk.CTkLabel(header, text=text, font=ctk.CTkFont(weight="bold")).grid(row=0, column=i, padx=6, sticky="w")

        self.batch_scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self.batch_scroll.grid(row=1, column=0, sticky="nsew", padx=16)

        footer = ctk.CTkFrame(panel, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", padx=16, pady=16)
        self.batch_total_label = ctk.CTkLabel(footer, text="Batch total: ₹0 · 0 rows")
        self.batch_total_label.pack(side="left")
        ctk.CTkButton(
            footer, text="Finalize & commit", fg_color="#1a7a4c", hover_color="#155f3b",
            command=self._commit_batch
        ).pack(side="right")

    def _refresh_batch_table(self):
        for w in self.batch_scroll.winfo_children():
            w.destroy()

        total = 0
        for idx, row in enumerate(self.batch):
            total += row["gross_value"]
            line = ctk.CTkFrame(self.batch_scroll, fg_color="transparent")
            line.pack(fill="x", pady=2)

            color = "#1a7a4c" if row["txn_type"] in ("BUY", "DEPOSIT") else "#b23b3b"
            ctk.CTkLabel(line, text=row["client_name"], width=100, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(line, text=row["txn_type"], text_color=color, width=80, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(line, text=row["display_symbol"], width=140, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(line, text=str(row.get("quantity", "")), width=60, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(line, text=str(row.get("price", "")), width=70, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(line, text=f"₹{row['gross_value']:,.2f}", width=90, anchor="w").pack(side="left", padx=6)
            ctk.CTkButton(
                line, text="✕", width=28, fg_color="transparent", text_color=("gray30", "gray70"),
                command=lambda i=idx: self._remove_from_batch(i)
            ).pack(side="left", padx=6)

        self.batch_total_label.configure(text=f"Batch total: ₹{total:,.2f} · {len(self.batch)} row(s)")

    def _remove_from_batch(self, index):
        del self.batch[index]
        self._refresh_batch_table()

    def _add_to_batch(self):
        client_id = self._selected_client_id()
        agent_id = self._selected_agent_id()
        client_name = self.client_dropdown.get()
        txn_type = self.txn_type_dropdown.get()

        if client_id is None:
            messagebox.showerror("Error", "Select a client first")
            return

        try:
            if txn_type == "BUY":
                row = {
                    "txn_type": "BUY",
                    "client_id": client_id, "client_name": client_name,
                    "agent_id": agent_id,
                    "segment": self.segment_dropdown.get(),
                    "symbol": self.symbol_entry.get().strip().upper(),
                    "quantity": int(self.quantity_entry.get()),
                    "price": float(self.price_entry.get()),
                    "entry_date": self.date_entry.get().strip(),
                    "manual_fee": float(self.manual_fee_entry.get()) if self.manual_fee_entry.get() else None,
                    "remarks": self.remarks_entry.get().strip() or None,
                }
                row["gross_value"] = gross_value(row["price"], row["quantity"])
                row["display_symbol"] = row["symbol"]

            elif txn_type == "SELL":
                open_trade = self._selected_open_trade()
                if open_trade is None:
                    messagebox.showerror("Error", "No open trade selected")
                    return
                exit_price = float(self.exit_price_entry.get())
                row = {
                    "txn_type": "SELL",
                    "client_id": client_id, "client_name": client_name,
                    "trade_id": open_trade.trade_id,
                    "quantity": open_trade.quantity,
                    "price": exit_price,
                    "exit_date": self.exit_date_entry.get().strip(),
                    "service_fee": float(self.service_fee_entry.get()) if self.service_fee_entry.get() else 0,
                    "manual_fee": float(self.sell_manual_fee_entry.get()) if self.sell_manual_fee_entry.get() else None,
                }
                row["gross_value"] = gross_value(exit_price, open_trade.quantity)
                row["display_symbol"] = f"Close {open_trade.symbol}"

            else:
                amount = float(self.cash_amount_entry.get())
                row = {
                    "txn_type": txn_type,
                    "client_id": client_id, "client_name": client_name,
                    "amount": amount,
                    "txn_date": self.cash_date_entry.get().strip(),
                    "remarks": self.cash_remarks_entry.get().strip() or None,
                    "gross_value": amount,
                    "display_symbol": "-",
                }

        except ValueError:
            messagebox.showerror("Error", "Check that quantity/price/amount fields contain valid numbers")
            return

        self.batch.append(row)
        self._refresh_batch_table()

    def _commit_batch(self):
        if not self.batch:
            return

        errors = []
        succeeded = []

        for row in self.batch:
            try:
                if row["txn_type"] == "BUY":
                    trade_service.open_trade(
                        client_id=row["client_id"], agent_id=row["agent_id"],
                        segment=row["segment"], symbol=row["symbol"],
                        quantity=row["quantity"], entry_date=row["entry_date"],
                        entry_price=row["price"], manual_brokerage=row["manual_fee"],
                        remarks=row["remarks"]
                    )
                elif row["txn_type"] == "SELL":
                    trade_service.close_trade(
                        trade_id=row["trade_id"], exit_date=row["exit_date"],
                        exit_price=row["price"], service_fee=row["service_fee"],
                        manual_brokerage=row["manual_fee"]
                    )
                elif row["txn_type"] == "DEPOSIT":
                    cash_service.deposit(row["client_id"], row["txn_date"], row["amount"], row["remarks"])
                elif row["txn_type"] == "WITHDRAWAL":
                    cash_service.withdraw(row["client_id"], row["txn_date"], row["amount"], row["remarks"])
                succeeded.append(row)
            except ValueError as e:
                errors.append(f"{row['display_symbol']}: {e}")

        for row in succeeded:
            self.batch.remove(row)
        self._refresh_batch_table()

        if errors:
            messagebox.showerror("Some rows failed", "\n".join(errors))
        else:
            messagebox.showinfo("Committed", f"{len(succeeded)} row(s) saved to database.")


def build(parent, app) -> ctk.CTkFrame:
    return DataEntryScreen(parent, app)
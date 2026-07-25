import customtkinter as ctk
from tkinter import messagebox

from app.services import client_service, agent_service, trade_service, cash_service
from app.domain.calculations.pnl import gross_value
from app.ui.widgets.date_picker import make_date_picker, set_date_value
from app.ui.theme import font, PRIMARY, PRIMARY_HOVER, SUCCESS, SUCCESS_HOVER, DANGER, DANGER_HOVER, BG_CARD, TEXT_MUTED
from app.ui.widgets.modal import Modal
from app.ui.widgets.data_table import DataTable

SEGMENTS = ["EQUITY", "FNO", "COMMODITY"]
TXN_TYPES = ["BUY", "SELL", "DEPOSIT", "WITHDRAWAL"]

BATCH_COLUMNS = [
    ("client", "Client", 110), ("type", "Type", 80), ("symbol", "Segment/Symbol", 140),
    ("qty", "Qty", 60), ("price", "Price", 80), ("gross", "Gross", 100),
]


class DataEntryScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.batch = app.session_state.setdefault("trade_batch", [])
        self.editing_index = None  # None = adding new row; int = editing batch[index]

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
        panel = ctk.CTkFrame(self, width=320, corner_radius=14, fg_color=BG_CARD)
        panel.grid(row=0, column=0, sticky="ns", padx=(0, 20))
        panel.grid_propagate(False)
        pad = {"padx": 20, "pady": (12, 0)}

        self.form_title = ctk.CTkLabel(panel, text="New transaction", font=font(16, "bold"))
        self.form_title.pack(anchor="w", padx=20, pady=(20, 0))

        ctk.CTkLabel(panel, text="Client", font=font(13)).pack(anchor="w", **pad)
        row = ctk.CTkFrame(panel, fg_color="transparent")
        row.pack(fill="x", padx=20)
        self.client_dropdown = ctk.CTkOptionMenu(row, values=["Loading..."], font=font(13),
                                                   fg_color=PRIMARY, button_color=PRIMARY_HOVER,
                                                   command=self._on_client_change)
        self.client_dropdown.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row, text="+ New", width=60, font=font(12), fg_color=PRIMARY,
                      hover_color=PRIMARY_HOVER, command=self._open_new_client_modal).pack(side="left", padx=(6, 0))

        ctk.CTkLabel(panel, text="Agent / Broker", font=font(13)).pack(anchor="w", **pad)
        row2 = ctk.CTkFrame(panel, fg_color="transparent")
        row2.pack(fill="x", padx=20)
        self.agent_dropdown = ctk.CTkOptionMenu(row2, values=["Loading..."], font=font(13),
                                                  fg_color=PRIMARY, button_color=PRIMARY_HOVER)
        self.agent_dropdown.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row2, text="+ New", width=60, font=font(12), fg_color=PRIMARY,
                      hover_color=PRIMARY_HOVER, command=self._open_new_agent_modal).pack(side="left", padx=(6, 0))

        seg_row = ctk.CTkFrame(panel, fg_color="transparent")
        seg_row.pack(fill="x", padx=20, pady=(12, 0))
        seg_col = ctk.CTkFrame(seg_row, fg_color="transparent")
        seg_col.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(seg_col, text="Segment", font=font(13)).pack(anchor="w")
        self.segment_dropdown = ctk.CTkOptionMenu(seg_col, values=SEGMENTS, font=font(13),
                                                     fg_color=PRIMARY, button_color=PRIMARY_HOVER)
        self.segment_dropdown.pack(fill="x")

        type_col = ctk.CTkFrame(seg_row, fg_color="transparent")
        type_col.pack(side="left", fill="x", expand=True, padx=(10, 0))
        ctk.CTkLabel(type_col, text="Txn type", font=font(13)).pack(anchor="w")
        self.txn_type_dropdown = ctk.CTkOptionMenu(type_col, values=TXN_TYPES, font=font(13),
                                                      fg_color=PRIMARY, button_color=PRIMARY_HOVER,
                                                      command=self._on_txn_type_change)
        self.txn_type_dropdown.pack(fill="x")

        self.dynamic_area = ctk.CTkFrame(panel, fg_color="transparent")
        self.dynamic_area.pack(fill="x", padx=20, pady=(12, 0))

        self.gross_value_label = ctk.CTkLabel(
            panel, text="Gross value\n₹0", font=font(13), justify="left",
            fg_color=("#EDF1FC", "#242938"), corner_radius=8
        )
        self.gross_value_label.pack(fill="x", padx=20, pady=(16, 0), ipady=8)

        btn_row = ctk.CTkFrame(panel, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(16, 8))
        self.primary_action_btn = ctk.CTkButton(
            btn_row, text="+ Add to batch", font=font(13, "bold"),
            fg_color=PRIMARY, hover_color=PRIMARY_HOVER, command=self._submit_form
        )
        self.primary_action_btn.pack(side="left", fill="x", expand=True)

        self.cancel_edit_btn = ctk.CTkButton(
            panel, text="Cancel edit", font=font(12), fg_color="transparent",
            border_width=1, text_color=TEXT_MUTED, command=self._cancel_edit
        )
        # only shown while editing -- packed/unpacked dynamically

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
        self.symbol_entry = ctk.CTkEntry(self.dynamic_area, placeholder_text="Symbol", font=font(13))
        self.symbol_entry.pack(fill="x", pady=(0, 8))

        qp_row = ctk.CTkFrame(self.dynamic_area, fg_color="transparent")
        qp_row.pack(fill="x", pady=(0, 8))
        self.quantity_entry = ctk.CTkEntry(qp_row, placeholder_text="Quantity", font=font(13))
        self.quantity_entry.pack(side="left", fill="x", expand=True)
        self.price_entry = ctk.CTkEntry(qp_row, placeholder_text="Price", font=font(13))
        self.price_entry.pack(side="left", fill="x", expand=True, padx=(6, 0))
        for e in (self.quantity_entry, self.price_entry):
            e.bind("<KeyRelease>", lambda _e: self._update_gross_preview())

        ctk.CTkLabel(self.dynamic_area, text="Entry date", font=font(12), text_color=TEXT_MUTED).pack(anchor="w")
        self.date_entry = make_date_picker(self.dynamic_area)
        self.date_entry.pack(fill="x", pady=(0, 8))
        self.manual_fee_entry = ctk.CTkEntry(self.dynamic_area, placeholder_text="Manual fee (optional)", font=font(13))
        self.manual_fee_entry.pack(fill="x", pady=(0, 8))
        self.remarks_entry = ctk.CTkEntry(self.dynamic_area, placeholder_text="Remarks", font=font(13))
        self.remarks_entry.pack(fill="x")
        self._update_gross_preview()

    def _build_sell_fields(self):
        ctk.CTkLabel(self.dynamic_area, text="Open trade to close", font=font(13)).pack(anchor="w")
        self.open_trade_dropdown = ctk.CTkOptionMenu(self.dynamic_area, values=["Select client first"],
                                                        font=font(13), fg_color=PRIMARY, button_color=PRIMARY_HOVER)
        self.open_trade_dropdown.pack(fill="x", pady=(0, 8))
        self._refresh_open_trades()

        self.exit_price_entry = ctk.CTkEntry(self.dynamic_area, placeholder_text="Exit price", font=font(13))
        self.exit_price_entry.pack(fill="x", pady=(0, 8))
        self.exit_price_entry.bind("<KeyRelease>", lambda _e: self._update_gross_preview())

        ctk.CTkLabel(self.dynamic_area, text="Exit date", font=font(12), text_color=TEXT_MUTED).pack(anchor="w")
        self.exit_date_entry = make_date_picker(self.dynamic_area)
        self.exit_date_entry.pack(fill="x", pady=(0, 8))
        self.service_fee_entry = ctk.CTkEntry(self.dynamic_area, placeholder_text="Service fee (optional)", font=font(13))
        self.service_fee_entry.pack(fill="x", pady=(0, 8))
        self.sell_manual_fee_entry = ctk.CTkEntry(self.dynamic_area, placeholder_text="Manual brokerage (optional)", font=font(13))
        self.sell_manual_fee_entry.pack(fill="x")
        self._update_gross_preview()

    def _build_cash_fields(self):
        self.cash_amount_entry = ctk.CTkEntry(self.dynamic_area, placeholder_text="Amount", font=font(13))
        self.cash_amount_entry.pack(fill="x", pady=(0, 8))
        self.cash_amount_entry.bind("<KeyRelease>", lambda _e: self._update_gross_preview())
        ctk.CTkLabel(self.dynamic_area, text="Date", font=font(12), text_color=TEXT_MUTED).pack(anchor="w")
        self.cash_date_entry = make_date_picker(self.dynamic_area)
        self.cash_date_entry.pack(fill="x", pady=(0, 8))
        self.cash_remarks_entry = ctk.CTkEntry(self.dynamic_area, placeholder_text="Remarks", font=font(13))
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

    # ---------- dropdown data ----------

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
        for i, t in enumerate(self.open_trades_for_client):
            if f"{t.symbol}  ({t.quantity} @ {t.entry_price})" == label:
                return self.open_trades_for_client[i]
        return None

    def _selected_open_trade_qty(self):
        t = self._selected_open_trade()
        return t.quantity if t else 0

    # ---------- + New modals ----------

    def _open_new_client_modal(self):
        modal = Modal(self.winfo_toplevel(), "New client", width=320, height=190)
        name_entry = modal.add_field("Client name", placeholder="e.g. Kailash")

        def save():
            try:
                client_service.create_client(name_entry.get())
                modal.destroy()
                self._refresh_clients()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        modal.add_buttons(save)
        name_entry.focus()

    def _open_new_agent_modal(self):
        modal = Modal(self.winfo_toplevel(), "New agent", width=320, height=260)
        name_entry = modal.add_field("Agent name", placeholder="e.g. Gagan")
        rate_entry = modal.add_field("Brokerage rate (%)", placeholder="e.g. 0.035")

        def save():
            try:
                rate = float(rate_entry.get())
                agent_service.create_agent(name_entry.get(), rate)
                modal.destroy()
                self._refresh_agents()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        modal.add_buttons(save)
        name_entry.focus()

    # ---------- RIGHT: BATCH TABLE ----------

    def _build_batch_panel(self):
        panel = ctk.CTkFrame(self, corner_radius=14, fg_color=BG_CARD)
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(panel, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        ctk.CTkLabel(header, text="Pending batch", font=font(16, "bold")).pack(side="left")
        ctk.CTkLabel(header, text="Click a row to edit it before committing", font=font(11),
                     text_color=TEXT_MUTED).pack(side="left", padx=(10, 0))

        table_wrap = ctk.CTkFrame(panel, fg_color="transparent")
        table_wrap.grid(row=1, column=0, sticky="nsew", padx=16)
        table_wrap.grid_rowconfigure(0, weight=1)
        table_wrap.grid_columnconfigure(0, weight=1)

        self.table = DataTable(table_wrap, BATCH_COLUMNS, on_row_select=self._load_row_for_edit)
        self.table.grid(row=0, column=0, sticky="nsew")

        footer = ctk.CTkFrame(panel, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", padx=16, pady=16)
        self.batch_total_label = ctk.CTkLabel(footer, text="Batch total: ₹0 · 0 rows", font=font(13))
        self.batch_total_label.pack(side="left")

        ctk.CTkButton(
            footer, text="Remove selected", font=font(13), fg_color=DANGER, hover_color=DANGER_HOVER,
            command=self._remove_selected
        ).pack(side="right", padx=(8, 0))
        self.commit_btn = ctk.CTkButton(
            footer, text="Finalize & commit", font=font(13, "bold"),
            fg_color=SUCCESS, hover_color=SUCCESS_HOVER, command=self._commit_batch
        )
        self.commit_btn.pack(side="right")

    def _refresh_batch_table(self):
        total = sum(r["gross_value"] for r in self.batch)
        rows = []
        for row in self.batch:
            rows.append((
                row["client_name"], row["txn_type"], row["display_symbol"],
                str(row.get("quantity", "")), str(row.get("price", "")),
                f"₹{row['gross_value']:,.2f}",
            ))
        self.table.set_rows(rows, row_data=list(range(len(self.batch))))
        self.batch_total_label.configure(text=f"Batch total: ₹{total:,.2f} · {len(self.batch)} row(s)")
        self.commit_btn.configure(state="normal" if self.batch else "disabled")

    def _remove_selected(self):
        selection = self.table.tree.selection()
        if not selection:
            return
        idx = self.table._row_data.get(selection[0])
        if idx is None:
            return
        del self.batch[idx]
        if self.editing_index == idx:
            self._cancel_edit()
        self._refresh_batch_table()

    # ---------- click row -> edit ----------

    def _load_row_for_edit(self, _item_id, index):
        if index is None or index >= len(self.batch):
            return
        row = self.batch[index]
        self.editing_index = index

        self.txn_type_dropdown.set(row["txn_type"])
        self._on_txn_type_change(row["txn_type"])

        client_match = next((c for c in self.clients if c.client_id == row["client_id"]), None)
        if client_match:
            self.client_dropdown.set(client_match.name)

        if row["txn_type"] == "BUY":
            agent_match = next((a for a in self.agents if a.agent_id == row["agent_id"]), None)
            if agent_match:
                self.agent_dropdown.set(agent_match.name)
            self.segment_dropdown.set(row["segment"])
            self.symbol_entry.insert(0, row["symbol"])
            self.quantity_entry.insert(0, str(row["quantity"]))
            self.price_entry.insert(0, str(row["price"]))
            set_date_value(self.date_entry, row["entry_date"])
            if row["manual_fee"] is not None:
                self.manual_fee_entry.insert(0, str(row["manual_fee"]))
            if row["remarks"]:
                self.remarks_entry.insert(0, row["remarks"])

        elif row["txn_type"] == "SELL":
            self._refresh_open_trades()
            self.exit_price_entry.insert(0, str(row["price"]))
            set_date_value(self.exit_date_entry, row["exit_date"])
            self.service_fee_entry.insert(0, str(row["service_fee"]))
            if row["manual_fee"] is not None:
                self.sell_manual_fee_entry.insert(0, str(row["manual_fee"]))

        else:
            self.cash_amount_entry.insert(0, str(row["amount"]))
            set_date_value(self.cash_date_entry, row["txn_date"])
            if row["remarks"]:
                self.cash_remarks_entry.insert(0, row["remarks"])

        self._update_gross_preview()
        self.form_title.configure(text=f"Editing row {index + 1}")
        self.primary_action_btn.configure(text="Update row")
        self.cancel_edit_btn.pack(fill="x", padx=20, pady=(0, 20))

    def _cancel_edit(self):
        self.editing_index = None
        self.form_title.configure(text="New transaction")
        self.primary_action_btn.configure(text="+ Add to batch")
        self.cancel_edit_btn.pack_forget()
        self.table.clear_selection()
        self._on_txn_type_change(self.txn_type_dropdown.get())

    # ---------- build row from form ----------

    def _build_row_from_form(self):
        client_id = self._selected_client_id()
        agent_id = self._selected_agent_id()
        client_name = self.client_dropdown.get()
        txn_type = self.txn_type_dropdown.get()

        if client_id is None:
            raise ValueError("Select a client first")

        if txn_type == "BUY":
            row = {
                "txn_type": "BUY", "client_id": client_id, "client_name": client_name,
                "agent_id": agent_id, "segment": self.segment_dropdown.get(),
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
                raise ValueError("No open trade selected")
            exit_price = float(self.exit_price_entry.get())
            row = {
                "txn_type": "SELL", "client_id": client_id, "client_name": client_name,
                "trade_id": open_trade.trade_id, "quantity": open_trade.quantity,
                "price": exit_price, "exit_date": self.exit_date_entry.get().strip(),
                "service_fee": float(self.service_fee_entry.get()) if self.service_fee_entry.get() else 0,
                "manual_fee": float(self.sell_manual_fee_entry.get()) if self.sell_manual_fee_entry.get() else None,
            }
            row["gross_value"] = gross_value(exit_price, open_trade.quantity)
            row["display_symbol"] = f"Close {open_trade.symbol}"

        else:
            amount = float(self.cash_amount_entry.get())
            row = {
                "txn_type": txn_type, "client_id": client_id, "client_name": client_name,
                "amount": amount, "txn_date": self.cash_date_entry.get().strip(),
                "remarks": self.cash_remarks_entry.get().strip() or None,
                "gross_value": amount, "display_symbol": "-",
            }
        return row

    def _submit_form(self):
        try:
            row = self._build_row_from_form()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        if self.editing_index is not None:
            self.batch[self.editing_index] = row
            self._cancel_edit()
        else:
            self.batch.append(row)

        self._refresh_batch_table()
        self._clear_dynamic_fields()

    def _clear_dynamic_fields(self):
        self._on_txn_type_change(self.txn_type_dropdown.get())

    # ---------- commit ----------

    def _commit_batch(self):
        if not self.batch:
            return
        errors, succeeded = [], []

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
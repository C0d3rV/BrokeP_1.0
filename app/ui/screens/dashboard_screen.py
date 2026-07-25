import customtkinter as ctk

from app.services import trade_service
from app.ui.theme import font, BG_CARD
from app.ui.async_utils import run_in_background


class DashboardScreen(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app

        ctk.CTkLabel(self, text="Welcome back, Broker", font=font(26, "bold")).pack(anchor="w")
        ctk.CTkLabel(self, text="Here's where things stand today.", font=font(14),
                     text_color=("gray30", "gray70")).pack(anchor="w", pady=(0, 16))

        self.stats_row = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_row.pack(fill="x", pady=(0, 16))
        self.open_card = self._stat_card("Open trades")
        self.closed_card = self._stat_card("Closed trades")
        self.pnl_card = self._stat_card("Net P&L (all time)")

        self.activity_frame = ctk.CTkFrame(self, corner_radius=14, fg_color=BG_CARD)
        self.activity_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(self.activity_frame, text="Recent activity", font=font(15, "bold")).pack(
            anchor="w", padx=16, pady=(14, 8)
        )
        self.activity_body = ctk.CTkFrame(self.activity_frame, fg_color="transparent")
        self.activity_body.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        self.on_show()

    def _stat_card(self, label):
        card = ctk.CTkFrame(self.stats_row, corner_radius=14, fg_color=BG_CARD)
        card.pack(side="left", fill="both", expand=True, padx=6)
        ctk.CTkLabel(card, text=label, font=font(13), text_color=("gray30", "gray70")).pack(
            anchor="w", padx=16, pady=(14, 2)
        )
        card.value_label = ctk.CTkLabel(card, text="…", font=font(20, "bold"))
        card.value_label.pack(anchor="w", padx=16, pady=(0, 14))
        return card

    def on_show(self):
        run_in_background(
            self,
            work_fn=lambda: (trade_service.list_all_open_trades(), trade_service.list_all_closed_trades()),
            on_done=self._apply_data
        )

    def _apply_data(self, result):
        if isinstance(result, Exception):
            return
        open_trades, closed_trades = result

        self.open_card.value_label.configure(text=str(len(open_trades)))
        self.closed_card.value_label.configure(text=str(len(closed_trades)))
        net_pl_total = sum(t.net_pl or 0 for t in closed_trades)
        self.pnl_card.value_label.configure(text=f"₹{net_pl_total:,.2f}")

        for w in self.activity_body.winfo_children():
            w.destroy()

        recent = sorted(open_trades + closed_trades, key=lambda t: t.entry_date, reverse=True)[:8]
        if not recent:
            ctk.CTkLabel(self.activity_body, text="No trades yet.", font=font(13),
                         text_color=("gray40", "gray60")).pack(anchor="w")
            return

        for t in recent:
            row = ctk.CTkFrame(self.activity_body, fg_color="transparent")
            row.pack(fill="x", pady=2)
            color = "#12805C" if t.status == "OPEN" else "#C0392B"
            ctk.CTkLabel(row, text=t.symbol, font=font(13), text_color=color, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=t.entry_date, font=font(13), anchor="e").pack(side="right")


def build(parent, app) -> ctk.CTkFrame:
    return DashboardScreen(parent, app)
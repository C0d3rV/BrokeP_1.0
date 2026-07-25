import customtkinter as ctk

from app.services import trade_service


def build(parent, app) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(parent, fg_color="transparent")

    ctk.CTkLabel(frame, text="Welcome back, Broker", font=ctk.CTkFont(size=26, weight="bold")).pack(anchor="w")
    ctk.CTkLabel(frame, text="Here's where things stand today.", text_color=("gray30", "gray70")).pack(
        anchor="w", pady=(0, 16)
    )

    open_trades = trade_service.list_all_open_trades()
    closed_trades = trade_service.list_all_closed_trades()

    stats_row = ctk.CTkFrame(frame, fg_color="transparent")
    stats_row.pack(fill="x", pady=(0, 16))

    def stat_card(parent, label, value):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.pack(side="left", fill="both", expand=True, padx=6)
        ctk.CTkLabel(card, text=label, text_color=("gray30", "gray70")).pack(anchor="w", padx=16, pady=(14, 2))
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", padx=16, pady=(0, 14))
        return card

    stat_card(stats_row, "Open trades", str(len(open_trades)))
    stat_card(stats_row, "Closed trades", str(len(closed_trades)))
    net_pl_total = sum(t.net_pl or 0 for t in closed_trades)
    stat_card(stats_row, "Net P&L (all time)", f"₹{net_pl_total:,.2f}")

    activity_frame = ctk.CTkFrame(frame, corner_radius=12)
    activity_frame.pack(fill="both", expand=True)
    ctk.CTkLabel(activity_frame, text="Recent activity", font=ctk.CTkFont(weight="bold")).pack(
        anchor="w", padx=16, pady=(14, 8)
    )

    recent = sorted(open_trades + closed_trades, key=lambda t: t.entry_date, reverse=True)[:8]
    if not recent:
        ctk.CTkLabel(activity_frame, text="No trades yet.", text_color=("gray40", "gray60")).pack(
            anchor="w", padx=16, pady=(0, 14)
        )
    else:
        for t in recent:
            row = ctk.CTkFrame(activity_frame, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=2)
            color = "#1a7a4c" if t.status == "OPEN" else "#b23b3b"
            ctk.CTkLabel(row, text=t.symbol, text_color=color, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=t.entry_date, anchor="e").pack(side="right")

    return frame
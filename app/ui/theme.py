import customtkinter as ctk
from tkinter import ttk

FONT_FAMILY = "Roboto"

# --- Palette ---
PRIMARY = "#3B5BDB"
PRIMARY_HOVER = "#2F4CC0"
SUCCESS = "#12805C"
SUCCESS_HOVER = "#0E6B4B"
DANGER = "#C0392B"
DANGER_HOVER = "#A5321F"

BG_APP = ("#F4F6FB", "#15171C")
BG_SIDEBAR = ("#1B1F2A", "#101218")
BG_CARD = ("#FFFFFF", "#1E212B")
BORDER = ("#D8DEE9", "#333844")
TEXT_PRIMARY = ("#1B1F2A", "#E8EAF0")
TEXT_MUTED = ("#5B6472", "#9BA3B4")

TREE_HEADER_BG = "#E3E8F7"
TREE_HEADER_FG = "#1B1F2A"
TREE_ROW_BG = "#FFFFFF"
TREE_ROW_ALT_BG = "#F5F7FC"
TREE_SELECT_BG = "#D6E0FB"
TREE_SELECT_FG = "#1B1F2A"


def font(size=14, weight="normal"):
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


def configure_ttk_style():
    """Call once, after the root Tk window exists (ttk.Style needs a live
    Tk instance). Styles ttk.Treeview to match the app's palette + Antic,
    since CTk itself has no native table widget."""
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(
        "Treeview",
        background=TREE_ROW_BG,
        fieldbackground=TREE_ROW_BG,
        foreground=TEXT_PRIMARY[0],
        rowheight=30,
        font=(FONT_FAMILY, 11),
        borderwidth=1,
        relief="solid",
    )
    style.map(
        "Treeview",
        background=[("selected", TREE_SELECT_BG)],
        foreground=[("selected", TREE_SELECT_FG)],
    )
    style.configure(
        "Treeview.Heading",
        background=TREE_HEADER_BG,
        foreground=TREE_HEADER_FG,
        font=(FONT_FAMILY, 11, "bold"),
        borderwidth=1,
        relief="solid",
    )
    style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
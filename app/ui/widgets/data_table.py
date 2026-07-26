import tkinter as tk
from tkinter import ttk
from app.ui.theme import TREE_ROW_BG, TREE_ROW_ALT_BG


class DataTable(ttk.Frame):
    def __init__(self, parent, columns, on_row_select=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.columns = columns
        self.on_row_select = on_row_select
        self._row_data = {}

        self.tree = ttk.Treeview(
            self, columns=[c[0] for c in columns], show="headings", selectmode="browse"
        )
        for key, header, width in columns:
            self.tree.heading(key, text=header)
            self.tree.column(key, width=width, minwidth=50, anchor="w", stretch=False)

        self.tree.tag_configure("evenrow", background=TREE_ROW_BG)
        self.tree.tag_configure("oddrow", background=TREE_ROW_ALT_BG)
        self.tree.tag_configure("profit", foreground="#12805C")
        self.tree.tag_configure("loss", foreground="#C0392B")

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        if self.on_row_select:
            self.tree.bind("<<TreeviewSelect>>", self._handle_select)

    def _handle_select(self, _event):
        selection = self.tree.selection()
        if not selection:
            return
        item_id = selection[0]
        self.on_row_select(item_id, self._row_data.get(item_id))

    def set_rows(self, rows, row_data=None):
        self.tree.delete(*self.tree.get_children())
        self._row_data = {}
        for i, row in enumerate(rows):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            extra_tag = row[-1] if isinstance(row[-1], str) and row[-1] in ("profit", "loss") else None
            tags = (tag, extra_tag) if extra_tag else (tag,)
            display_row = row[:-1] if extra_tag else row
            item_id = self.tree.insert("", "end", values=display_row, tags=tags)
            if row_data is not None:
                self._row_data[item_id] = row_data[i]

    def clear_selection(self):
        self.tree.selection_remove(self.tree.selection())

    def clear(self):
        self.tree.delete(*self.tree.get_children())
        self._row_data = {}
import customtkinter as ctk
from app.ui.theme import font, PRIMARY, PRIMARY_HOVER, BG_CARD, TEXT_MUTED


class Modal(ctk.CTkToplevel):
    def __init__(self, parent, title: str, width=340, height=220):
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.resizable(False, False)
        self.configure(fg_color=BG_CARD)

        self._center_over_parent(width, height)

        self.transient(parent)
        self.lift()
        self.focus_force()
        self.grab_set()
        self.after(10, self.focus_force)

        self.bind("<Escape>", lambda e: self.destroy())

        self.body = ctk.CTkFrame(self, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=20, pady=20)

    def _center_over_parent(self, width, height):
        self.update_idletasks()
        px, py = self.parent.winfo_rootx(), self.parent.winfo_rooty()
        pw, ph = self.parent.winfo_width(), self.parent.winfo_height()
        x = px + (pw - width) // 2
        y = py + (ph - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def add_field(self, label_text, placeholder=""):
        ctk.CTkLabel(self.body, text=label_text, font=font(13)).pack(anchor="w", pady=(6, 2))
        entry = ctk.CTkEntry(self.body, placeholder_text=placeholder, font=font(13), height=36)
        entry.pack(fill="x")
        return entry

    def add_buttons(self, on_save, save_label="Save"):
        row = ctk.CTkFrame(self.body, fg_color="transparent")
        row.pack(fill="x", pady=(18, 0))
        ctk.CTkButton(row, text="Cancel", font=font(13), fg_color="transparent",
                      border_width=1, text_color=TEXT_MUTED,
                      command=self.destroy).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(row, text=save_label, font=font(13, "bold"), fg_color=PRIMARY,
                      hover_color=PRIMARY_HOVER, command=on_save).pack(side="left", fill="x", expand=True, padx=(6, 0))
        self.bind("<Return>", lambda e: on_save())
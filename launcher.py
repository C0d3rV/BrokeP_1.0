import os
from app.database.schema import create_all_tables
from app.ui.main_window import MainWindow
from app.utils.font_loader import load_bundled_font
import customtkinter as ctk


def main():
    font_path = os.path.join(os.path.dirname(__file__), "assets", "fonts", "Antic-Regular.ttf")
    load_bundled_font(font_path)  # silently no-ops if the file is missing

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    create_all_tables()

    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
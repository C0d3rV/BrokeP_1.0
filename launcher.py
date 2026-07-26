import os
import sys
from app.database.schema import create_all_tables
from app.ui.main_window import MainWindow
from app.utils.font_loader import load_bundled_font
import customtkinter as ctk

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    # Safely resolve font path for both normal run and compiled exe
    font_path = resource_path(os.path.join("assets", "fonts", "Antic-Regular.ttf"))
    load_bundled_font(font_path)  # silently no-ops if the file is missing

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    create_all_tables()

    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
from app.database.schema import create_all_tables
from app.ui.main_window import MainWindow
import customtkinter as ctk


def main():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    create_all_tables()

    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
# BrokeP: Lightweight & Fully Offline Trade Ledger

**BrokeP** is a fast, offline-first desktop application built for professional traders, independent financial consultants, and family offices.

Managing multiple trading accounts, calculating advisory fees, and tracking daily profits can quickly turn into a messy spreadsheet nightmare. BrokeP solves this by giving you a clean, unified dashboard to handle all your bookkeeping effortlessly. It replaces complicated Excel files with a system that automatically tracks your cash flow, open positions, and total returns.

Built to be **100% offline and highly lightweight**, BrokeP replaces bloated, cloud-based subscriptions with a snappy local app. Your financial data never leaves your machine—guaranteeing absolute privacy, zero server latency, and total control over your records.

---

## Key Features & Core Calculations

* **100% Offline & Private:** No internet connection required. No cloud syncing, no data harvesting, and no subscriptions. Built entirely on a serverless SQLite architecture, all financial data remains securely stored on your local hard drive.
* **Ultra-Lightweight Performance:** Unlike heavy web-wrapped applications, BrokeP is natively compiled. It consumes minimal RAM and CPU, ensuring snappy, instant-load performance even on older hardware.
* **Multi-Entity Ledger Management:** Easily track trades, cash transfers, and historical adjustments across multiple clients or sub-accounts from a single, centralized dashboard.
* **Advanced P&L Analytics (MTM):** Moving beyond basic bookkeeping, the app automatically calculates Gross P&L, Net P&L, historical realized gains, and live unrealized gains based on daily Mark-to-Market (MTM) closing prices.
* **Service Fee Bookkeeping:** Built-in calculation engines accurately process standard transactional costs, complex split-fee structures, and custom advisory or platform fees.
* **Institutional-Grade Reporting:**
* **PDF Exports:** Generate beautiful, cinematic-styled Daily Snapshots and Historical Trade Ledgers instantly.
* **CSV Exports:** Dump raw, clean, unformatted trade data directly into CSV for external pivot tables and advanced spreadsheet analysis.



---

## 📸 Application Interface
*(Note: The trades, symbols, clients, and financial figures shown in the screenshots below are for representational purposes only.)*

### Dashboard & Daily Mark-to-Market
<img width="1920" height="1080" alt="Home page" src="https://github.com/user-attachments/assets/8fede410-1756-4493-9779-f490021f229c" />
Provides a real-time snapshot of open positions, total capital invested, and unrealized P&L based on daily closing prices.


### Batch Trade Entry
<img width="1920" height="1080" alt="Entry page" src="https://github.com/user-attachments/assets/484ab435-c762-476b-a99e-8872c8d31931" />
A streamlined data entry interface for logging new trades, calculating fees, and staging pending batches before committing them to the ledger.


### Historical Reports & Exports
<img width="1920" height="1080" alt="Report page" src="https://github.com/user-attachments/assets/977ee0b2-862b-492c-8a31-4a6eb709963c" />
Filter trades by client, segment, or date range to generate detailed ledger views. Instantly export data to clean CSVs or formatted PDFs.


---

## 🏗️ Architecture & Code Structure

BrokeP is engineered using a clean, layered architectural pattern (Model-View-Controller/Service-Repository) to ensure high maintainability, testability, and a strict separation of concerns.

* **UI Layer (Views):** Built with CustomTkinter, this layer strictly handles user interactions, input validation, and rendering the modern dark/light mode interface. It does not process business logic directly.
* **Service Layer (Backend Logic):** Acts as the brain of the application. It receives requests from the UI and executes complex business rules, such as P&L calculations, Mark-to-Market processing, and orchestrating PDF/CSV data exports.
* **Data Repository Layer:** Manages all data persistence. It abstracts raw SQLite queries into clean Python objects, ensuring the Service Layer never has to write SQL directly. This makes the database highly modular and secure.

---

## 🛠️ Tech Stack

* **Core Logic:** Python 3
* **User Interface:** CustomTkinter (built on standard Tkinter for minimal overhead)
* **Database:** SQLite3 (Serverless, zero-configuration)
* **PDF Generation:** ReportLab
* **Data Export:** Python native `csv` module
* **Packaging:** PyInstaller & Inno Setup

---

## 💻 Installation (Development)

1. **Clone the repository:**
```bash
git clone https://github.com/YourUsername/BrokeP.git
cd BrokeP

```


2. **Create and activate a virtual environment:**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

```


3. **Install dependencies:**
```bash
pip install -r requirements.txt

```


4. **Run the application:**
```bash
python main.py

```



---

## 📦 Building the Executable (Production)

To package BrokeP into a standalone, lightweight Windows executable, we use PyInstaller to create a highly optimized directory build, which can then be wrapped into a professional installer using Inno Setup.

Run the following PyInstaller command to compile the app, attach the logo, and bundle required assets:

```bash
pyinstaller --noconfirm --windowed --onedir --name "BrokeP" --icon="assets/icons/logo.ico" --add-data "assets/icons/logo.ico;assets/icons" --collect-all customtkinter --collect-all reportlab --collect-all tzdata main.py

```

Once built, point **Inno Setup** to the generated `dist/BrokeP` directory to create a secure, offline `setup.exe` for end users.

---

## ⚖️ Legal Disclaimer

**BrokeP is purely a technology solution for offline accounting and data management.** 
This software is not a registered financial institution or trading platform. It does not interface with live market exchanges to execute trades, nor does it hold, route, or manage real financial assets or client funds. BrokeP does not provide financial, investment, or legal advice. The application is provided "as is" for informational and bookkeeping purposes only. Users are solely responsible for ensuring that their application of this software—including the generation of invoices or calculation of service and advisory fees—fully complies with the applicable laws, regulatory frameworks, and licensing requirements in their local jurisdictions. 

**Non-Commercial Use Only:** BrokeP is provided strictly for personal, internal, or educational use. It is not authorized for commercial redistribution, resale, white-labeling, or to be offered as a hosted software-as-a-service (SaaS).

*All sample data, ticker symbols, and financial figures displayed in promotional materials or screenshots are entirely fictional and for representational purposes only.*

---

## 📄 License

This project is released under a **Custom Non-Commercial License**. 

You are free to download, install, and modify the software for your own personal or internal business bookkeeping. However, you may not redistribute, repackage, sell, or use the source code (or any compiled executables) for direct commercial gain or public commercial distribution without explicit written permission from the author.

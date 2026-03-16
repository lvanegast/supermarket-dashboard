import pandas as pd
import sqlite3
from pathlib import Path

# Absolute paths based on this file's location
_BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = _BASE_DIR / "data" / "SuperMarket.csv"
DB_DIR = _BASE_DIR / "database"
DB_PATH = DB_DIR / "sales.db"


def load_csv_to_sqlite():
    if not DATA_PATH.exists():
        print(f"ERROR: CSV file not found at {DATA_PATH}")
        return

    # Create database directory if it doesn't exist
    DB_DIR.mkdir(exist_ok=True)

    # Read CSV
    df = pd.read_csv(DATA_PATH)

    # Connect to SQLite
    conn = sqlite3.connect(DB_PATH)

    # Write table
    df.to_sql("sales", conn, if_exists="replace", index=False)

    conn.close()
    print("Data loaded successfully into SQLite.")


if __name__ == "__main__":
    load_csv_to_sqlite()

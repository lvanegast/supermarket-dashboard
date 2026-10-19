"""ETL script to load source CSV into both DuckDB and SQLite engines."""
from pathlib import Path
import sqlite3
import pandas as pd

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False

_BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = _BASE_DIR / "data" / "SuperMarket.csv"
DB_DIR = _BASE_DIR / "database"
SQLITE_PATH = DB_DIR / "sales.db"
DUCKDB_PATH = DB_DIR / "sales.duckdb"


def load_all():
    """Load CSV into SQLite and DuckDB."""
    if not DATA_PATH.exists():
        print(f"ERROR: CSV file not found at {DATA_PATH}")
        return False

    DB_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_PATH)

    # 1. SQLite
    conn = sqlite3.connect(SQLITE_PATH)
    df.to_sql("sales", conn, if_exists="replace", index=False)
    conn.close()
    print(f"[OK] SQLite database updated: {SQLITE_PATH}")

    # 2. DuckDB
    if DUCKDB_AVAILABLE:
        con = duckdb.connect(str(DUCKDB_PATH))
        con.execute(f"CREATE OR REPLACE TABLE sales AS SELECT * FROM read_csv_auto('{DATA_PATH.as_posix()}')")
        con.close()
        print(f"[OK] DuckDB database updated: {DUCKDB_PATH}")

    return True


if __name__ == "__main__":
    load_all()

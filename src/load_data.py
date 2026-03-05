import pandas as pd
import sqlite3
from pathlib import Path

# Paths absolutos basados en la ubicación de este archivo
_BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = _BASE_DIR / "data" / "SuperMarket.csv"
DB_DIR = _BASE_DIR / "database"
DB_PATH = DB_DIR / "sales.db"


def load_csv_to_sqlite():
    if not DATA_PATH.exists():
        print(f"ERROR: No se encontró el archivo CSV en {DATA_PATH}")
        return

    # Crear directorio de base de datos si no existe
    DB_DIR.mkdir(exist_ok=True)

    # Leer CSV
    df = pd.read_csv(DATA_PATH)

    # Conectar a SQLite
    conn = sqlite3.connect(DB_PATH)

    # Guardar la tabla
    df.to_sql("sales", conn, if_exists="replace", index=False)

    conn.close()
    print("Datos cargados correctamente en SQLite.")


if __name__ == "__main__":
    load_csv_to_sqlite()

import pandas as pd
import sqlite3
import os

# Paths
DATA_PATH = os.path.join("data", "SuperMarket.csv")   # Ajusta el nombre si es distinto
DB_PATH = os.path.join("database", "sales.db")

def load_csv_to_sqlite():
    # Leer CSV
    df = pd.read_csv(DATA_PATH)

    # Conectar a SQLite
    conn = sqlite3.connect(DB_PATH)

    # Guardar la tabla
    df.to_sql("sales", conn, if_exists="replace", index=False)

    conn.close()
    print("✔ Datos cargados correctamente en SQLite.")

if __name__ == "__main__":
    load_csv_to_sqlite()

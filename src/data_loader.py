import pandas as pd

COLUMNS: list = [
    "placa",
    "fecha_revision",
    "telefono"
]


def load_data(file_path: str) -> pd.DataFrame:
    """Carga el archivo de ventas desde Excel."""
    return pd.read_csv(
        file_path,
        sep=";",
        encoding="utf-8",
        skip_blank_lines=True,
        engine="python"
    ).dropna(
        how="all"
    )[COLUMNS]
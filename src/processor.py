import pandas as pd
import re
from datetime import datetime, timedelta


def extract_plate(doc_fuente: str) -> str:
    """
    Extrae la placa de un texto dado. Si no cumple el formato estándar,
    retorna el texto completo.
    
    Args:
        doc_fuente (str): El texto de la columna 'Doc. Fuente'.
    
    Returns:
        str: La placa extraída o el texto completo si no se detecta una placa válida.
    """
        
    pattern = r'\b[A-Z]{3}\d{3}\b|\b[A-Z]{3}\d{2}[A-Z]\b'
    match = re.findall(pattern, doc_fuente)
    if match:
        return match[0]
    return doc_fuente


def get_clients_for_messages(
        df: pd.DataFrame, 
        days_before: int = 3
    ) -> pd.DataFrame:
    
    df = df.copy()    
    current_date = pd.to_datetime(datetime.now().date())

    df["Fecha"] = pd.to_datetime(df["Fecha"], format="%Y/%m/%d").dt.date  # Convertir a date
    df["fecha_vencimiento"] = (pd.to_datetime(df["Fecha"]) + timedelta(days=365)).dt.date  # Convertir a date
    df["fecha_notificacion"] = (pd.to_datetime(df["Fecha"]) + timedelta(days=(365 - days_before))).dt.date  # Convertir a date
    df["dias_vencidos"] = (pd.to_datetime(df["fecha_notificacion"]) - pd.to_datetime(current_date)).dt.days
    
    df['Placa'] = df['Doc. Fuente'].apply(extract_plate)
    df["valid_number"] = df["Beneficiario Celular"].apply(lambda x: bool(re.match(r'^\d{10}$', str(x))))

    # Retornar solo los registros que cumplen la condición (cambiar a == 0 en producción)
    return df[df["dias_vencidos"] == 0].reset_index(drop=True)


def extract_message_parameters(df: pd.DataFrame) -> pd.DataFrame:
    required_columns = ["Beneficiario Celular", "Placa", "fecha_vencimiento", "valid_number"]
    
    if not all(col in df.columns for col in required_columns):
        raise ValueError("El DataFrame no tiene las columnas requeridas.")
    
    # Retornar solo las filas que tienen placa válida y fecha de vencimiento válida
    return df[["Beneficiario Nombre", "Beneficiario Celular", "Placa", "fecha_vencimiento", "valid_number"]]


# def extract_message_parameters(clients: pd.DataFrame) -> list:
#     parameters = []
#     for idx, row in clients.iterrows():
#         try:
#             nombre = row["Beneficiario Nombre"]
#             celular = row["Beneficiario Celular"]
#             placa = row["Placa"]
#             fecha_vencimiento = row["fecha_vencimiento"].strftime("%Y-%m-%d")

#             if pd.notna(celular) and pd.notna(placa) and pd.notna(fecha_vencimiento):
#                 parameters.append({
#                     "nombre": nombre,
#                     "celular": str(int(celular)),
#                     "placa": placa,
#                     "fecha_vencimiento": fecha_vencimiento
#                 })
        
#         except Exception as e:
#             print(f"Error procesando fila {idx}: {e}")
#             continue

#     return parameters

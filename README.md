# CDA Urrao - Notificador Técnico Mecánica por WhatsApp

Este proyecto permite identificar clientes cuya técnico-mecánica está próxima a vencerse (1 año - 3 días desde la compra) y enviarles un mensaje por WhatsApp de manera automatizada o simulada.

---

## Estructura del proyecto

cda_urrao/
├── app.py                     # Script principal para correr la app con Streamlit
├── requirements.txt          # Librerías necesarias
├── .env                      # Variables sensibles como tokens de Twilio
├── README.md                 # Instrucciones del proyecto
├── venv/                     # Entorno virtual (no se sube al repo)
│
├── data/
│   └── Ventas_Consulta2024.xls  # Archivo original de ventas
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py        # Funciones para cargar datos desde Excel
│   ├── notifier.py           # Lógica para enviar mensajes por WhatsApp
│   ├── processor.py          # Lógica para calcular fechas de vencimiento
│   └── ui.py                 # Elementos visuales de Streamlit
│
└── logs/
    └── app.log               # (opcional) Registro de errores o eventos

| Archivo            | Descripción                                                                                |
| ------------------ | ------------------------------------------------------------------------------------------- |
| `app.py`         | Orquesta todo desde Streamlit, llama funciones desde `src/`.                              |
| `data_loader.py` | Lee el Excel, limpia columnas y devuelve un `DataFrame`.                                  |
| `processor.py`   | Calcula la fecha de vencimiento y filtra clientes que deben ser notificados.                |
| `notifier.py`    | Envía los mensajes o los simula (puede usar Twilio o `print`).                           |
| `ui.py`          | Encapsula los elementos visuales de Streamlit, si queremos dividir la lógica de interfaz.  |
| `.env`           | Guarda credenciales como el SID/token de Twilio o un flag de entorno (`MODO=desarrollo`). |

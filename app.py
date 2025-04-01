import os 
import logging
import streamlit as st

from src.data_loader import load_data
from src.processor import get_clients_for_messages, extract_message_parameters
from src.notifier import send_message
from datetime import datetime
from dotenv import load_dotenv


# Cargar variables desde el archivo .env
load_dotenv()

TOKEN = os.getenv("TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

st.set_page_config(
    page_title="CDA Nariño", 
    layout="centered"
)

st.title("📢 Notificador Técnico-Mecánica - CDA Nariño")
st.write(
    "Identifica clientes cuya técnico-mecánica está por vencer y permite notificarles por WhatsApp."
)

# --- Configuración ---
DAYS_BEFORE: int = 3
FILE_NAME: str = 'rtcmyec_consolidado_2024.csv'
INPUT_FOLDER: str = "./data_source"
TEMPLATE_NAME: str = 'cda_narino_notifications'

base_dir = os.getcwd()
file_path = os.path.abspath(os.path.join(base_dir, INPUT_FOLDER, FILE_NAME))

# Logging
day_log: str = datetime.now().strftime("%d_%m_%Y")
log_file_path = f"./logs/{day_log}.log"

logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# Inicializar variables de estado global
if "clients" not in st.session_state:
    st.session_state["clients"] = None

if 'token' not in st.session_state:
    st.session_state.token = None

# --- Botón 1: Verificar clientes ---
if st.button("🔍 Verificar clientes a contactar"):
    try:
        data = load_data(file_path)
        clients = get_clients_for_messages(
            df=data, 
            days_before=DAYS_BEFORE
        )

        if clients.empty:
            st.info("✅ No hay clientes para contactar en este momento.")
        else:
            valid_clients = clients[clients["valid_number"] == True]
            invalid_clients = clients[clients["valid_number"] == False]

            st.success(f"🔔 Se encontraron {valid_clients.shape[0]} cliente(s) válidos que deben ser contactados.")
            st.warning(f"⚠️ Se encontraron {invalid_clients.shape[0]} cliente(s) sin número de celular válido o vacío.")
            
            st.dataframe(valid_clients, use_container_width=True)
            
            if not invalid_clients.empty:
                st.write("Clientes sin número de celular válido:")
                st.dataframe(invalid_clients, use_container_width=True)
            
            st.session_state.clients = valid_clients
            st.session_state.invalid_clients = invalid_clients

    except Exception as e:
        st.error("❌ Error al procesar los datos.")
        logger.exception("Error en verificación de clientes")


# Entrada para el token
if st.session_state.clients is not None:
    st.session_state.token = st.text_input("🔑 Ingrese su Token de Acceso (Bearer Token)", type="password")

# --- Botón 2: Enviar mensajes ---
if st.session_state.clients is not None:
    if st.button("📨 Enviar mensajes (WhatsApp)"):
        try:
            if not st.session_state.token:
                st.error("❌ Ingrese un Token válido antes de continuar.")
                logger.error("❌ Token no ingresado por el usuario.")
            else:
                logger.info(f"📨 Inicio del proceso de envío de mensajes a {len(st.session_state.clients)} clientes.")
                clients_with_params = extract_message_parameters(st.session_state.clients)
                
                if clients_with_params.empty:
                    st.info("📭 No se encontraron parámetros válidos para enviar mensajes.")
                    logger.info("📭 No se encontraron parámetros válidos para enviar mensajes.")
                else:
                    successful_messages = 0
                    successful_clients = []

                    for idx, row in clients_with_params.iterrows():
                        if row["valid_number"]:  
                            celular = str(row["telefono"])
                            if not celular.startswith("57"):
                                celular = f"57{celular}"
                            
                            try:
                                response = send_message(
                                    token=st.session_state.token,
                                    phone_number_id=PHONE_NUMBER_ID,
                                    recipient_number=celular,
                                    placa=row["placa"],
                                    vigencia=row["fecha_vencimiento"].strftime("%Y-%m-%d"),
                                    template_name=TEMPLATE_NAME
                                )

                                if response.get("messages"):
                                    successful_messages += 1
                                    successful_clients.append(f"{row['placa']} ({celular})")
                                    st.write(f"✅ Mensaje enviado a {row['placa']} - Número: {celular}")
                                    logger.info(f"✅ Mensaje enviado a {row['Beneficiario Nombre']} - Placa: {row['placa']} - Número: {celular} - Vigencia: {row['fecha_vencimiento']}")

                                else:
                                    error_message = response.get("error", {}).get("message", "Error desconocido")
                                    st.error(f"❌ Error al enviar mensaje a {row['placa']}: {error_message}")
                                    logger.error(f"❌ Error al enviar mensaje a {row['placa']} ({celular}): {error_message}")

                            except Exception as e:
                                error_message = str(e)
                                st.error(f"❌ Error al enviar mensaje a {row['placa']}: {error_message}")
                                logger.error(f"❌ Error al enviar mensaje a {row['placa']} ({celular}): {error_message}")

                    
                    if successful_messages > 0:
                        st.success(f"✅ Se enviaron {successful_messages} mensajes exitosamente.")
                        st.write("### 📋 Resumen de mensajes enviados:")
                        for client in successful_clients:
                            st.write(f"- {client}")
                        
                        logger.info(f"📋 Resumen: {successful_messages} mensajes enviados exitosamente.")

        except Exception as e:
            st.error("❌ Error al enviar los mensajes.")
            logger.exception("Error al enviar mensajes")

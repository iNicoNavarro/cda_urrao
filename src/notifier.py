# src/notifier.py

import requests
import logging

def send_message(
        token: str, 
        phone_number_id: str, 
        recipient_number: str, 
        placa: str, 
        vigencia: str, 
        template_name: str
    ):

    """
    Envía un mensaje de WhatsApp usando la API de Meta.

    Args:
        token (str): Token de acceso de Meta (permanente o temporal).
        phone_number_id (str): ID del número de teléfono configurado en Meta.
        recipient_number (str): Número de WhatsApp del destinatario en formato internacional (ej: "573175576781").
        placa (str): Placa del vehículo.
        vigencia (str): Fecha de vencimiento de la técnico mecánica.
        template_name (str): Nombre de la plantilla aprobada en Meta.
    """
    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {"code": "es_CO"},
            "components": [
                {
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": placa},
                        {"type": "text", "text": vigencia}
                    ]
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        logging.info(f"✅ Mensaje enviado exitosamente a {recipient_number}.")
    else:
        logging.error(f"❌ Error al enviar mensaje: {response.status_code} - {response.text}")
    
    return response.json()

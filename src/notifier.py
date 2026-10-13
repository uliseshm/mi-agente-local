import os
import requests
from dotenv import load_dotenv

load_dotenv()

NTFY_SERVER = os.getenv("NTFY_SERVER", "https://ntfy.sh")
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "ollama_local_agent")

def send_notification(title: str, message: str, priority: int = 3, tags: list = None):
    """
    Envía una notificación push a través de ntfy.sh asegurando codificación UTF-8 en los headers.
    Prioridades: 1 (min), 2 (low), 3 (default), 4 (high), 5 (urgent)
    """
    url = f"{NTFY_SERVER}/{NTFY_TOPIC}"
    
    # Codificamos el título en UTF-8 para evitar errores de latin-1 con emojis y tildes
    encoded_title = title.encode('utf-8').decode('latin-1')
    
    headers = {
        "Title": encoded_title,
        "Priority": str(priority)
    }

    if tags:
        headers["Tags"] = ",".join(tags)

    try:
        response = requests.post(
            url, 
            data=message.encode('utf-8'), 
            headers=headers, 
            timeout=5
        )
        if response.status_code == 200:
            print(f"📣 Notificación enviada con éxito a ntfy.sh ({NTFY_TOPIC}): {title}")
            return True
        else:
            print(f"⚠️ Error al enviar notificación ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"❌ Excepción en envío de notificación: {e}")
        return False

if __name__ == "__main__":
    # Prueba individual del notificador con título en español y emoji
    send_notification(
        title="Prueba de Agente Local",
        message="¡Si lees esto, tu canal de notificaciones ntfy está funcionando correctamente!",
        tags=["bell", "robot"]
    )
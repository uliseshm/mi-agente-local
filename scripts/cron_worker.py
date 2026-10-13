import os
import sys

# Agregar la carpeta 'src' al path para poder importar módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from database import get_pending_reminders, mark_task_notified
from notifier import send_notification

def check_and_notify():
    """Busca tareas vencidas o en hora actual y dispara las notificaciones."""
    pending_tasks = get_pending_reminders()

    if not pending_tasks:
        print("🕒 [Cron Worker] Sin recordatorios pendientes en este minuto.")
        return

    print(f"🔔 [Cron Worker] Se encontraron {len(pending_tasks)} recordatorio(s) pendiente(s)!")

    for task in pending_tasks:
        title = f"⏰ Recordatorio: {task['title']}"
        body = f"Proyecto: {task['project_name']}\n"
        if task['description']:
            body += f"Detalles: {task['description']}\n"
        body += f"Fecha programada: {task['due_date']}"

        # Enviar vía ntfy
        success = send_notification(
            title=title,
            message=body,
            priority=4,
            tags=["alarm_clock", "calendar"]
        )

        # Si se envió con éxito (o en cada revisión), marcamos para evitar duplicados
        if success:
            mark_task_notified(task['id'])
            print(f"✅ Tarea ID {task['id']} actualizada a estado 'NOTIFIED'.")

if __name__ == "__main__":
    check_and_notify()
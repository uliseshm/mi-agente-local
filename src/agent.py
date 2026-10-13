import os
import json
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from ollama import Client
from dotenv import load_dotenv
from database import add_task, init_db

load_dotenv()

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# Cliente de Ollama
client = Client(host=OLLAMA_HOST)

# Definición del esquema estricto con Pydantic
class TaskExtraction(BaseModel):
    title: str = Field(description="Título corto y claro de la tarea o recordatorio")
    description: Optional[str] = Field(default="", description="Detalles adicionales si los hay")
    due_date: Optional[str] = Field(
        default=None, 
        description="Fecha y hora de vencimiento en formato exacto 'YYYY-MM-DD HH:MM:SS'. Si no especifica hora, asumir 09:00:00"
    )
    project_name: str = Field(
        default="General", 
        description="Nombre del proyecto o categoría (ej. General, Personal, Trabajo, Portfolio)"
    )

def parse_user_intent(user_input: str) -> TaskExtraction:
    """Procesa el texto del usuario con Ollama y extrae los datos estructurados."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S (%A)")

    system_prompt = f"""
    Eres un asistente ejecutor de tareas. Tu objetivo es extraer la intención del usuario y estructurarla en un formato de tarea.
    
    INFORMACIÓN CONTEXTUAL DEL TIEMPO REAL:
    - Fecha y hora actual del sistema: {now_str}

    REGLAS STRICTAS:
    1. Resuelve fechas relativas ("hoy", "mañana", "el viernes", "en 3 horas") basándote en la fecha y hora actual dada arriba.
    2. El campo 'due_date' DEBE estar formateado estrictamente como 'YYYY-MM-DD HH:MM:SS'.
    3. Si el usuario no menciona una hora específica para un día, usa las '09:00:00'.
    4. Si el mensaje es solo una nota o tarea sin fecha, deja 'due_date' como null.
    5. Retorna ÚNICAMENTE la estructura JSON correspondiente al esquema.
    """

    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        format=TaskExtraction.model_json_schema(), # Forzar JSON Schema
        options={"temperature": 0.1} # Temperatura baja para menor alucinación
    )

    # Convertir respuesta en objeto Pydantic
    content = response['message']['content']
    data = json.loads(content)
    return TaskExtraction(**data)

def process_prompt_and_save(user_input: str):
    """Procesa el texto del usuario, extrae la tarea y la guarda en la base de datos."""
    print(f"\n🗣️ Entrada del usuario: \"{user_input}\"")
    print("🤖 Procesando con Ollama...")

    try:
        extracted = parse_user_intent(user_input)
        print("💡 Estructura extraída:")
        print(f"   - Título: {extracted.title}")
        print(f"   - Fecha/Hora límite: {extracted.due_date}")
        print(f"   - Proyecto: {extracted.project_name}")
        print(f"   - Descripción: {extracted.description}")

        task_id = add_task(
            title=extracted.title,
            due_date=extracted.due_date,
            description=extracted.description,
            project_name=extracted.project_name
        )
        print(f"✅ Tarea guardada con éxito en SQLite (ID: {task_id})")
        return task_id

    except Exception as e:
        print(f"❌ Error al procesar la entrada: {e}")
        return None

if __name__ == "__main__":
    init_db()
    # Pruebas manuales
    process_prompt_and_save("Recuérdame pagar la luz mañana a las 5pm")
    process_prompt_and_save("Comprar café para la oficina")
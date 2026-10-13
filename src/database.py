import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH", "./data/tasks.db")

def get_connection():
    """Crea y retorna una conexión a la base de datos SQLite."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conn

def init_db():
    """Inicializa las tablas de la base de datos si no existen."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla de Proyectos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Tabla de Tareas y Recordatorios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        due_date DATETIME,
        status TEXT CHECK(status IN ('PENDING', 'NOTIFIED', 'COMPLETED', 'CANCELLED')) DEFAULT 'PENDING',
        project_id INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
    )
    """)

    # Proyecto por defecto
    cursor.execute("""
    INSERT OR IGNORE INTO projects (id, name, description) 
    VALUES (1, 'General', 'Proyecto por defecto para tareas cotidianas')
    """)

    conn.commit()
    conn.close()
    print("✅ Base de datos e índices inicializados correctamente.")

def add_task(title: str, due_date: str = None, description: str = "", project_name: str = "General"):
    """Inserta una nueva tarea asociada a un proyecto."""
    conn = get_connection()
    cursor = conn.cursor()

    # Obtener id del proyecto (o usar General)
    cursor.execute("SELECT id FROM projects WHERE name = ?", (project_name,))
    row = cursor.fetchone()
    project_id = row['id'] if row else 1

    cursor.execute("""
    INSERT INTO tasks (title, description, due_date, status, project_id)
    VALUES (?, ?, ?, 'PENDING', ?)
    """, (title, description, due_date, project_id))

    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id

def get_pending_reminders():
    """Obtiene las tareas pendientes cuya fecha/hora limite ya venció o es la hora actual."""
    conn = get_connection()
    cursor = conn.cursor()
    now_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    SELECT t.id, t.title, t.description, t.due_date, p.name as project_name
    FROM tasks t
    LEFT JOIN projects p ON t.project_id = p.id
    WHERE t.status = 'PENDING' 
      AND t.due_date IS NOT NULL 
      AND t.due_date <= ?
    """, (now_iso,))

    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_task_notified(task_id: int):
    """Actualiza el estado de una tarea a NOTIFIED para no duplicar alertas."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = 'NOTIFIED' WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
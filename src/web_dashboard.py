import os
import sys
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Incluir carpeta src en el path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_connection, init_db
from agent import process_prompt_and_save

load_dotenv()

app = FastAPI(title="Local AI Task Agent API")

templates = Jinja2Templates(directory="src/templates")

class PromptRequest(BaseModel):
    prompt: str

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/tasks")
def list_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT t.id, t.title, t.description, t.due_date, t.status, p.name as project_name
        FROM tasks t
        LEFT JOIN projects p ON t.project_id = p.id
        ORDER BY t.id DESC
    """)
    tasks = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return tasks

@app.post("/api/process")
def process_prompt(data: PromptRequest):
    if not data.prompt.strip():
        raise HTTPException(status_code=400, detail="El prompt no puede estar vacío")
    
    task_id = process_prompt_and_save(data.prompt)
    if not task_id:
        raise HTTPException(status_code=500, detail="Error al procesar el mensaje con el LLM local")
    
    return {"status": "success", "task_id": task_id}

@app.put("/api/tasks/{task_id}/complete")
def complete_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = 'COMPLETED' WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"status": "updated"}

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("web_dashboard:app", host="0.0.0.0", port=port, reload=True)
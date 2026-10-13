# 🤖 Local AI Assistant & Task Scheduler

Un asistente virtual local, privado y ligero construido con **Python**, **Ollama**, **FastAPI**, **SQLite** y **ntfy.sh**. Este proyecto procesa lenguaje natural para extraer intenciones, gestionar proyectos y programar recordatorios de forma determinista, combinando la flexibilidad de los LLMs locales con la fiabilidad de automatizaciones en segundo plano.

---

## 🌟 Características Principales

- **100% Local y Privado:** Inferencia de lenguaje natural ejecutada completamente en local con Ollama (`llama3.2:3b`), manteniendo tu información personal y tareas privadas.
- **Structured Outputs (JSON Estructurado):** Procesamiento de mensajes en español (ej. *"Recuérdame revisar el avance del portafolio mañana a las 4pm"*) con extracción de fechas relativas normalizadas a formato ISO 8601 (`YYYY-MM-DD HH:MM:SS`).
- **Arquitectura Desacoplada y Confiable:** La lógica de programación y notificaciones se delega a un trabajador determinista de Linux (`cron`), evitando dependencia del tiempo real en la IA.
- **Notificaciones Push Multidispositivo:** Integración con webhooks de `ntfy.sh` para alertas instantáneas en móviles (Android/iOS) y navegadores web.
- **Dashboard Web Moderno:** Interfaz interactiva construida con **FastAPI**, **Jinja2** y **Tailwind CSS** para enviar solicitudes en lenguaje natural y gestionar tareas y proyectos en tiempo real.
- **Contenerización e Infraestructura:** Entorno estandarizado listo para desplegar con **Docker Compose** en Linux / WSL 2.

---

## 🏗️ Arquitectura del Sistema

```text
[ Usuario / Web Dashboard UI ]
              │
              ▼
    [ src/web_dashboard.py ]
              │
              ▼
      [ src/agent.py ] ──────(Structured JSON)──────► [ Ollama (LLM Local) ]
              │
              ▼
       [ SQLite DB ] ◄────── Persistencia de Proyectos y Tareas (PENDING)
              ▲
              │ (Lectura periódica cada minuto)
    [ scripts/cron_worker.py ]
              │
              ▼
     [ src/notifier.py ] ────(HTTP Webhook)────► [ ntfy.sh ] ────► [ Móvil / Desktop ]
```

## 🛠️ Tecnologías Utilizadas
Lenguaje: Python 3.12+

Framework Web & API: FastAPI, Uvicorn, Jinja2

Motor LLM Local: Ollama (llama3.2:3b) con validación de esquemas vía Pydantic

Base de Datos: SQLite3

Notificaciones: ntfy.sh REST API

Infraestructura: Docker / Docker Compose / WSL 2 (Ubuntu) / Cron


## 🚀 Guía de Instalación y Despliegue
Prerrequisitos
- WSL 2 (Ubuntu/Linux) o Linux nativo.

- Docker y Docker Compose habilitados.

- Python 3.10+ e instalador venv.

1. Clonar el repositorio y configurar el entorno
```bash
git clone [https://github.com/tu_usuario/local-ai-agent-tasks.git](https://github.com/tu_usuario/local-ai-agent-tasks.git)
cd local-ai-agent-tasks

# Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

2. Variables de entorno
Copia la plantilla .env.example a .env y ajusta tu tema de notificaciones único:
cp .env.example .env

3. Iniciar el servicio de Ollama (Docker)
docker compose -f docker/docker-compose.yml up -d

# Descargar el modelo liviano recomendando
docker exec -it local_ai_ollama ollama run llama3.2:3b

4. Inicializar la Base de Datos y ejecutar la Web UI
python3 src/web_dashboard.py

Abre tu navegador e ingresa a http://localhost:8000.

5. Configurar el trabajador de automatización (Cron)
Para habilitar las revisiones automáticas de notificaciones cada minuto, añade la siguiente regla a tu crontab:
crontab -e

Agrega la línea (ajustando tus rutas de usuario):
* * * * * cd /home/tu_usuario/local-ai-agent-tasks && /home/tu_usuario/local-ai-agent-tasks/venv/bin/python3 scripts/cron_worker.py >> /tmp/agent_cron.log 2>&1


📂 Estructura del Proyecto
```text
local-ai-agent-tasks/
├── config/                  # Configuraciones del proyecto
├── data/                    # Volumen persistente SQLite (tasks.db)
├── docker/
│   └── docker-compose.yml   # Orquestación del motor de Ollama
├── scripts/
│   └── cron_worker.py       # Tarea en segundo plano para verificación de alertas
├── src/
│   ├── agent.py             # Integración con Ollama, Prompts y Pydantic
│   ├── database.py          # Conexión y operaciones CRUD en SQLite
│   ├── notifier.py          # Cliente HTTP para ntfy.sh
│   ├── web_dashboard.py     # Servidor API FastAPI
│   └── templates/
│       └── index.html       # Dashboard UI en Tailwind CSS
├── .env.example             # Plantilla de variables de entorno
├── crontab.example          # Plantilla para tareas programadas
├── requirements.txt         # Dependencias de Python
└── README.md                # Documentación del proyecto
```
---

### 📌 Paso Final: Subir a tu Repositorio de GitHub

Asegúrate de no subir la base de datos local ni el entorno virtual. Puedes crear o revisar tu archivo `.gitignore`:

```text
venv/
__pycache__/
*.pyc
data/*.db
.env


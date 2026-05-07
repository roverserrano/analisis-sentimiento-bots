# SentinelAI

SentinelAI es una plataforma web academica para analizar comentarios de redes sociales con dos modelos XLM-RoBERTa ya entrenados:

| Modelo | Tarea | Clases |
|---|---|---|
| `sentiment_model` | Clasificacion de sentimiento | Bueno / Regular / Malo |
| `bot_model` | Deteccion de bot | Bot / No bot |

El proyecto no reentrena modelos. El objetivo es integrar modelos locales de Hugging Face dentro de una aplicacion web funcional con FastAPI y React.

## Estructura

```text
project-root/
├── backend/
│   ├── main.py
│   ├── .env.example
│   ├── requirements.txt
│   ├── routes/
│   │   ├── __init__.py
│   │   └── analysis.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── model_service.py
│   ├── models/
│   │   ├── README.md
│   │   ├── sentiment_model/
│   │   └── bot_model/
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py
│   └── utils/
│       ├── __init__.py
│       └── preprocessor.py
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   ├── package.json
│   ├── .env.example
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       ├── components/
│       ├── pages/
│       ├── charts/
│       └── services/
├── .gitignore
└── README.md
```

## Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Coloca tus modelos en models/sentiment_model/ y models/bot_model/
uvicorn main:app --reload
```

## Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## URLs locales

- Frontend: http://localhost:5173
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Modelos locales

Cada modelo debe tener estructura Hugging Face:

```text
backend/models/sentiment_model/
  config.json
  tokenizer.json
  pytorch_model.bin
  tokenizer_config.json
  special_tokens_map.json

backend/models/bot_model/
  config.json
  tokenizer.json
  pytorch_model.bin
  tokenizer_config.json
  special_tokens_map.json
```

Tambien se acepta `model.safetensors`.

Si los modelos no estan disponibles, FastAPI arranca en modo degradado para que la plataforma pueda demostrarse. Para exigir modelos reales, cambia en `backend/.env`:

```bash
ALLOW_DEGRADED_MODE=false
```

## Endpoints

| Metodo | Ruta | Descripcion |
|---|---|---|
| GET | `/` | Informacion de la API |
| GET | `/api/health` | Estado del servicio y modelos |
| POST | `/api/analyze` | Analizar un comentario |
| POST | `/api/analyze/bulk` | Analizar lista de comentarios |
| POST | `/api/analyze/csv` | Analizar CSV subido |

### Analisis individual

Request:

```json
{
  "comentario": "El servicio fue excelente, me atendieron muy rapido."
}
```

Response:

```json
{
  "comentario": "El servicio fue excelente, me atendieron muy rapido.",
  "sentimiento": {
    "clase": "Bueno",
    "confianza": 0.94,
    "probabilidades": {
      "Bueno": 0.94,
      "Regular": 0.04,
      "Malo": 0.02
    }
  },
  "bot": {
    "clase": "No bot",
    "confianza": 0.87,
    "probabilidades": {
      "No bot": 0.87,
      "Bot": 0.13
    }
  }
}
```

### Analisis masivo

Request:

```json
{
  "comentarios": [
    "Excelente atencion.",
    "El servicio fue lento.",
    "Gana premios gratis en este link!!! #promo #gratis #viral"
  ]
}
```

Response:

```json
{
  "total": 3,
  "resultados": [],
  "resumen": {
    "distribucion_sentimiento": {
      "Bueno": 1,
      "Regular": 1,
      "Malo": 1
    },
    "distribucion_bot": {
      "No bot": 2,
      "Bot": 1
    },
    "confianza_promedio_sentimiento": 0.82,
    "confianza_promedio_bot": 0.79,
    "total_analizados": 3,
    "errores": 0
  }
}
```

## CSV

El archivo CSV debe incluir una columna llamada `comentario`:

```csv
comentario
El servicio fue excelente.
No recomiendo la atencion.
Click aqui y gana premios gratis!!! #promo #viral
```

## Variables de entorno

Backend:

```bash
SENTIMENT_MODEL_PATH=models/sentiment_model
BOT_MODEL_PATH=models/bot_model
SENTIMENT_LABELS=Bueno,Regular,Malo
BOT_LABELS=No bot,Bot
MAX_TEXT_LENGTH=512
MODEL_MAX_TOKENS=192
ALLOW_DEGRADED_MODE=true
```

Frontend:

```bash
VITE_API_BASE_URL=
```

El frontend usa proxy Vite: las llamadas van a `/api/...` y Vite las redirige a `http://localhost:8000`.

## Verificacion

Backend:

```bash
cd backend
python -m py_compile main.py routes/analysis.py services/model_service.py schemas/schemas.py utils/preprocessor.py
```

Frontend:

```bash
cd frontend
npm run lint
npm run build
```


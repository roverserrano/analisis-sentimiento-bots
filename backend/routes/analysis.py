from io import StringIO

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile

from schemas.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    BulkAnalysisRequest,
    BulkAnalysisResponse,
    HealthResponse,
)
from services.model_service import ModelServiceError, model_service


router = APIRouter(prefix="/api", tags=["analisis"])
MAX_BULK_COMMENTS = 500


def _build_summary(results: list[dict], errors: int = 0) -> dict:
    """Calcula estadisticas agregadas para el modo masivo."""
    sentiment_distribution = {"Bueno": 0, "Regular": 0, "Malo": 0}
    bot_distribution = {"No bot": 0, "Bot": 0}

    sentiment_confidence = 0.0
    bot_confidence = 0.0

    for item in results:
        sentiment = item["sentimiento"]
        bot = item["bot"]
        sentiment_distribution[sentiment["clase"]] = (
            sentiment_distribution.get(sentiment["clase"], 0) + 1
        )
        bot_distribution[bot["clase"]] = bot_distribution.get(bot["clase"], 0) + 1
        sentiment_confidence += sentiment["confianza"]
        bot_confidence += bot["confianza"]

    total = len(results)
    return {
        "distribucion_sentimiento": sentiment_distribution,
        "distribucion_bot": bot_distribution,
        "confianza_promedio_sentimiento": round(sentiment_confidence / total, 4)
        if total
        else 0,
        "confianza_promedio_bot": round(bot_confidence / total, 4) if total else 0,
        "total_analizados": total,
        "errores": errors,
    }


def _validate_bulk_size(comments: list[str]) -> None:
    if len(comments) > MAX_BULK_COMMENTS:
        raise HTTPException(
            status_code=400,
            detail=f"El limite maximo es {MAX_BULK_COMMENTS} comentarios por solicitud.",
        )


@router.get("/health", response_model=HealthResponse)
def health() -> dict:
    return model_service.health()


@router.post("/analyze", response_model=AnalysisResponse)
def analyze(payload: AnalysisRequest) -> dict:
    try:
        return model_service.analyze(payload.comentario)
    except ModelServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/analyze/bulk", response_model=BulkAnalysisResponse)
def analyze_bulk(payload: BulkAnalysisRequest) -> dict:
    _validate_bulk_size(payload.comentarios)

    results = []
    errors = 0

    for comment in payload.comentarios:
        try:
            results.append(model_service.analyze(comment))
        except Exception:
            errors += 1

    if not results:
        raise HTTPException(
            status_code=400,
            detail="No se pudo analizar ningun comentario valido.",
        )

    return {
        "total": len(results),
        "resultados": results,
        "resumen": _build_summary(results, errors),
    }


@router.post("/analyze/csv", response_model=BulkAnalysisResponse)
async def analyze_csv(file: UploadFile = File(...)) -> dict:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="El archivo debe tener extension .csv.")

    raw_content = await file.read()
    if not raw_content:
        raise HTTPException(status_code=400, detail="El archivo CSV esta vacio.")

    try:
        csv_text = raw_content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="El CSV debe estar codificado en UTF-8.") from exc

    try:
        dataframe = pd.read_csv(StringIO(csv_text))
    except Exception as exc:
        raise HTTPException(status_code=400, detail="No se pudo leer el archivo CSV.") from exc

    if "comentario" not in dataframe.columns:
        raise HTTPException(
            status_code=400,
            detail="El CSV debe incluir una columna llamada 'comentario'.",
        )

    comments = [
        str(value).strip()
        for value in dataframe["comentario"].dropna().tolist()
        if str(value).strip()
    ]

    if not comments:
        raise HTTPException(
            status_code=400,
            detail="La columna 'comentario' no contiene textos validos.",
        )

    _validate_bulk_size(comments)

    results = []
    errors = 0
    for comment in comments:
        try:
            results.append(model_service.analyze(comment))
        except Exception:
            errors += 1

    return {
        "total": len(results),
        "resultados": results,
        "resumen": _build_summary(results, errors),
    }


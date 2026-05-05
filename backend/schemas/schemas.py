from pydantic import BaseModel, Field, field_validator


class AnalysisRequest(BaseModel):
    comentario: str = Field(..., min_length=1, max_length=2000)

    @field_validator("comentario")
    @classmethod
    def clean_comment(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("El comentario no puede estar vacio.")
        return cleaned


class BulkAnalysisRequest(BaseModel):
    comentarios: list[str] = Field(..., min_length=1, max_length=500)

    @field_validator("comentarios")
    @classmethod
    def clean_comments(cls, value: list[str]) -> list[str]:
        cleaned = [comment.strip() for comment in value if comment and comment.strip()]
        if not cleaned:
            raise ValueError("Debe enviar al menos un comentario valido.")
        return cleaned


class Prediction(BaseModel):
    clase: str
    confianza: float = Field(..., ge=0, le=1)
    probabilidades: dict[str, float]


class AnalysisResponse(BaseModel):
    comentario: str
    sentimiento: Prediction
    bot: Prediction


class BulkSummary(BaseModel):
    distribucion_sentimiento: dict[str, int]
    distribucion_bot: dict[str, int]
    confianza_promedio_sentimiento: float
    confianza_promedio_bot: float
    total_analizados: int
    errores: int


class BulkAnalysisResponse(BaseModel):
    total: int
    resultados: list[AnalysisResponse]
    resumen: BulkSummary


class HealthResponse(BaseModel):
    status: str
    modelos_cargados: bool
    modo_degradado: bool
    dispositivo: str
    sentiment_model_path: str
    bot_model_path: str
    error: str | None = None


import os
import re
import json
from pathlib import Path
from typing import Any

from utils.preprocessor import preprocess_text


class ModelServiceError(RuntimeError):
    pass


class ModelService:
    """Singleton responsable de cargar modelos y ejecutar inferencia."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        self._initialized = True
        self.base_dir = Path(__file__).resolve().parents[1]
        self.sentiment_model_path = self._resolve_path(
            os.getenv("SENTIMENT_MODEL_PATH", "models/sentiment_model")
        )
        self.bot_model_path = self._resolve_path(os.getenv("BOT_MODEL_PATH", "models/bot_model"))
        self.sentiment_labels = self._parse_labels(
            os.getenv("SENTIMENT_LABELS"),
            ["Bueno", "Regular", "Malo"],
        )
        self.bot_labels = self._parse_labels(os.getenv("BOT_LABELS"), ["No bot", "Bot"])
        self.max_text_length = int(os.getenv("MAX_TEXT_LENGTH", "512"))
        self.model_max_tokens = int(os.getenv("MODEL_MAX_TOKENS", "192"))
        self.allow_degraded_mode = self._parse_bool(os.getenv("ALLOW_DEGRADED_MODE", "true"))

        self.device = "cpu"
        self.torch = None
        self.sentiment_tokenizer = None
        self.sentiment_model = None
        self.bot_tokenizer = None
        self.bot_model = None
        self.loaded = False
        self.degraded = False
        self.load_error = ""
        self.sentiment_active_path = self.sentiment_model_path
        self.bot_active_path = self.bot_model_path

    def _resolve_path(self, value: str) -> Path:
        path = Path(value)
        return path if path.is_absolute() else self.base_dir / path

    @staticmethod
    def _parse_bool(value: str | None) -> bool:
        if value is None:
            return False
        return value.strip().lower() in {"1", "true", "yes", "si", "on"}

    @staticmethod
    def _parse_labels(value: str | None, default: list[str]) -> list[str]:
        if not value:
            return default
        labels = [item.strip() for item in value.split(",") if item.strip()]
        return labels or default

    @staticmethod
    def _has_model_files(path: Path) -> bool:
        weight_files = {"pytorch_model.bin", "model.safetensors", "tf_model.h5"}
        return path.exists() and (path / "config.json").exists() and any(
            (path / file_name).exists() for file_name in weight_files
        )

    @staticmethod
    def _checkpoint_number(path: Path) -> int:
        match = re.search(r"checkpoint-(\d+)$", path.name)
        return int(match.group(1)) if match else -1

    def _resolve_model_dir(self, base_path: Path) -> Path:
        """
        Devuelve el directorio del modelo listo para cargar:
        1) Si el path ya tiene artefactos HF, se usa tal cual.
        2) Si no, intenta usar el checkpoint-* mas alto dentro del path.
        """
        if self._has_model_files(base_path):
            return base_path

        checkpoint_dirs = [
            item
            for item in base_path.glob("checkpoint-*")
            if item.is_dir() and self._has_model_files(item)
        ]
        if checkpoint_dirs:
            checkpoint_dirs.sort(key=self._checkpoint_number, reverse=True)
            return checkpoint_dirs[0]

        return base_path

    @staticmethod
    def _load_label_mappings(path: Path, fallback: list[str], task: str) -> list[str]:
        """
        Carga mapeos de etiquetas personalizados desde label_mappings.json cuando existe.
        Soporta formato:
        - {"0":"Bueno","1":"Regular","2":"Malo"}
        - {"id2label":{"0":"Bueno","1":"Regular","2":"Malo"}}
        """
        mapping_file = path / "label_mappings.json"
        if not mapping_file.exists():
            return fallback

        try:
            payload = json.loads(mapping_file.read_text(encoding="utf-8"))
        except Exception:
            return fallback

        id2label = payload.get("id2label", payload) if isinstance(payload, dict) else {}
        if not isinstance(id2label, dict):
            return fallback

        pairs = []
        for key, value in id2label.items():
            try:
                pairs.append((int(key), str(value)))
            except Exception:
                continue

        if not pairs:
            return fallback

        pairs.sort(key=lambda item: item[0])
        labels = [ModelService._normalize_label(label, task) for _, label in pairs]
        return labels or fallback

    def load_models(self) -> None:
        """Carga ambos modelos. Si falla y esta permitido, activa modo degradado."""
        if self.loaded or self.degraded:
            return

        try:
            self.sentiment_active_path = self._resolve_model_dir(self.sentiment_model_path)
            self.bot_active_path = self._resolve_model_dir(self.bot_model_path)

            if not self._has_model_files(self.sentiment_active_path):
                raise ModelServiceError(
                    f"No se encontro el modelo de sentimiento en {self.sentiment_model_path}."
                )
            if not self._has_model_files(self.bot_active_path):
                raise ModelServiceError(f"No se encontro el modelo de bot en {self.bot_model_path}.")

            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            self.torch = torch
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

            self.sentiment_tokenizer = AutoTokenizer.from_pretrained(
                self.sentiment_active_path,
                local_files_only=True,
            )
            self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(
                self.sentiment_active_path,
                local_files_only=True,
            ).to(self.device)
            self.sentiment_model.eval()
            self.sentiment_labels = self._labels_from_config(
                self.sentiment_model,
                self.sentiment_labels,
                "sentimiento",
            )
            self.sentiment_labels = self._load_label_mappings(
                self.sentiment_active_path,
                self.sentiment_labels,
                "sentimiento",
            )

            self.bot_tokenizer = AutoTokenizer.from_pretrained(
                self.bot_active_path,
                local_files_only=True,
            )
            self.bot_model = AutoModelForSequenceClassification.from_pretrained(
                self.bot_active_path,
                local_files_only=True,
            ).to(self.device)
            self.bot_model.eval()
            self.bot_labels = self._labels_from_config(self.bot_model, self.bot_labels, "bot")
            self.bot_labels = self._load_label_mappings(
                self.bot_active_path,
                self.bot_labels,
                "bot",
            )

            self.loaded = True
            self.degraded = False
            self.load_error = ""
        except Exception as exc:
            self.loaded = False
            self.load_error = str(exc)

            if not self.allow_degraded_mode:
                raise ModelServiceError(f"No se pudieron cargar los modelos: {exc}") from exc

            self.degraded = True

    def _labels_from_config(self, model: Any, fallback: list[str], task: str) -> list[str]:
        id2label = getattr(model.config, "id2label", {}) or {}
        num_labels = int(getattr(model.config, "num_labels", len(fallback)))
        labels = []

        for index in range(num_labels):
            configured = id2label.get(index) or id2label.get(str(index))
            label = configured or (fallback[index] if index < len(fallback) else f"Clase {index}")
            if str(label).upper() == f"LABEL_{index}":
                label = fallback[index] if index < len(fallback) else label
            labels.append(self._normalize_label(str(label), task))

        return labels

    @staticmethod
    def _normalize_label(label: str, task: str) -> str:
        normalized = label.strip().lower().replace("_", " ").replace("-", " ")

        if task == "sentimiento":
            mapping = {
                "good": "Bueno",
                "positive": "Bueno",
                "positivo": "Bueno",
                "neutral": "Regular",
                "neutro": "Regular",
                "bad": "Malo",
                "negative": "Malo",
                "negativo": "Malo",
            }
        else:
            mapping = {
                "human": "No bot",
                "not bot": "No bot",
                "no bot": "No bot",
                "bot": "Bot",
                "generated": "Bot",
            }

        return mapping.get(normalized, label.strip())

    def analyze(self, comment: str) -> dict:
        text = preprocess_text(comment, max_length=self.max_text_length)
        if not text:
            raise ValueError("El comentario no puede estar vacio.")

        if self.loaded:
            sentiment = self._predict_with_model(
                text,
                self.sentiment_tokenizer,
                self.sentiment_model,
                self.sentiment_labels,
            )
            bot = self._predict_with_model(text, self.bot_tokenizer, self.bot_model, self.bot_labels)
        elif self.degraded:
            sentiment = self._predict_sentiment_degraded(text)
            bot = self._predict_bot_degraded(text)
        else:
            raise ModelServiceError("Los modelos no estan cargados.")

        return {
            "comentario": comment.strip(),
            "sentimiento": sentiment,
            "bot": bot,
        }

    def _predict_with_model(self, text: str, tokenizer: Any, model: Any, labels: list[str]) -> dict:
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=self.model_max_tokens,
        )
        inputs = {key: value.to(self.device) for key, value in inputs.items()}

        with self.torch.no_grad():
            outputs = model(**inputs)
            probabilities_tensor = self.torch.softmax(outputs.logits, dim=-1)[0]

        probabilities = probabilities_tensor.detach().cpu().tolist()
        best_index = int(max(range(len(probabilities)), key=probabilities.__getitem__))
        probability_map = {
            labels[index]: round(float(probability), 4)
            for index, probability in enumerate(probabilities)
            if index < len(labels)
        }

        return {
            "clase": labels[best_index],
            "confianza": round(float(probabilities[best_index]), 4),
            "probabilidades": probability_map,
        }

    def _predict_sentiment_degraded(self, text: str) -> dict:
        positive_words = {
            "excelente",
            "bueno",
            "buen",
            "genial",
            "rapido",
            "recomendado",
            "gracias",
            "perfecto",
            "feliz",
        }
        negative_words = {
            "malo",
            "pesimo",
            "horrible",
            "lento",
            "problema",
            "queja",
            "demora",
            "fallo",
            "estafa",
        }
        tokens = set(re.findall(r"\w+", text.lower()))
        positives = len(tokens & positive_words)
        negatives = len(tokens & negative_words)

        if positives > negatives:
            probabilities = {"Bueno": 0.78, "Regular": 0.15, "Malo": 0.07}
        elif negatives > positives:
            probabilities = {"Bueno": 0.08, "Regular": 0.17, "Malo": 0.75}
        else:
            probabilities = {"Bueno": 0.22, "Regular": 0.61, "Malo": 0.17}

        return self._prediction_from_probs(probabilities)

    def _predict_bot_degraded(self, text: str) -> dict:
        lowered = text.lower()
        words = re.findall(r"\w+", lowered)
        unique_ratio = len(set(words)) / max(len(words), 1)
        suspicious_score = 0
        suspicious_score += lowered.count("http://") + lowered.count("https://") + lowered.count("www.")
        suspicious_score += 1 if lowered.count("#") >= 3 else 0
        suspicious_score += 1 if lowered.count("@") >= 3 else 0
        suspicious_score += 1 if re.search(r"([!?])\1{2,}", text) else 0
        suspicious_score += sum(
            term in lowered for term in ("promo", "gratis", "click", "gana", "oferta", "link")
        )
        suspicious_score += 1 if len(words) > 35 and unique_ratio < 0.55 else 0

        probabilities = (
            {"No bot": 0.25, "Bot": 0.75}
            if suspicious_score >= 3
            else {"No bot": 0.82, "Bot": 0.18}
        )
        return self._prediction_from_probs(probabilities)

    @staticmethod
    def _prediction_from_probs(probabilities: dict[str, float]) -> dict:
        label = max(probabilities, key=probabilities.get)
        return {
            "clase": label,
            "confianza": round(float(probabilities[label]), 4),
            "probabilidades": {key: round(float(value), 4) for key, value in probabilities.items()},
        }

    def health(self) -> dict:
        return {
            "status": "ok" if self.loaded or self.degraded else "error",
            "modelos_cargados": self.loaded,
            "modo_degradado": self.degraded,
            "dispositivo": self.device,
            "sentiment_model_path": str(self.sentiment_model_path),
            "bot_model_path": str(self.bot_model_path),
            "sentiment_model_activo": str(self.sentiment_active_path),
            "bot_model_activo": str(self.bot_active_path),
            "error": self.load_error or None,
        }


model_service = ModelService()

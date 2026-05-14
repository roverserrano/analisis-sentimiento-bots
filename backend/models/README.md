# Modelos de SentinelAI

Coloca los modelos entrenados en estas rutas:

```text
backend/models/sentiment_model/
backend/models/bot_model/
```

Cada carpeta puede tener los archivos finales en la raiz:

```text
config.json
model.safetensors (o pytorch_model.bin)
tokenizer.json
tokenizer_config.json
label_mappings.json (opcional, recomendado)
```

Tambien se soporta estructura con checkpoints:

```text
sentiment_model/
  checkpoint-3750/
  checkpoint-5625/
bot_model/
  checkpoint-1174/
  checkpoint-1761/
```

Si hay varios `checkpoint-*`, el backend usa automaticamente el mas alto (ultimo).

`label_mappings.json` puede tener:

```json
{
  "id2label": {
    "0": "Bueno",
    "1": "Regular",
    "2": "Malo"
  }
}
```

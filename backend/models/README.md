# Modelos de SentinelAI

Coloca aqui los modelos XLM-RoBERTa exportados con formato Hugging Face.

## Estructura esperada

```text
models/
  sentiment_model/
    config.json
    tokenizer.json
    pytorch_model.bin
    tokenizer_config.json
    special_tokens_map.json
  bot_model/
    config.json
    tokenizer.json
    pytorch_model.bin
    tokenizer_config.json
    special_tokens_map.json
```

El backend tambien reconoce `model.safetensors`.


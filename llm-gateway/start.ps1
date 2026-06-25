# Inicia o LLM Gateway (LiteLLM proxy) na porta 4000
# Pré-requisito: Ollama rodando em http://localhost:11434

$env:LITELLM_LOG = "INFO"
litellm --config config.yaml --port 4000 --host 0.0.0.0

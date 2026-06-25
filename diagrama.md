# Diagrama de Arquitetura — Entrega 1 (Fundação)

```mermaid
graph TD
    U([Cliente HTTP]) -->|POST /chat| AS

    subgraph "Entrega 1 — Local, sem containers"
        AS["agent-service\nFastAPI :8000"]
        GW["llm-gateway\nLiteLLM :4000"]
        OL["Ollama\n:11434\nllama3.2"]
        NS["name-server\nEureka :8761"]
    end

    AS -->|"GET /chat/completions\n(OpenAI-compat.)"| GW
    GW -->|"POST /api/chat"| OL
    AS -.->|"registro heartbeat"| NS

    style AS fill:#a8d8ea,stroke:#333
    style GW fill:#f9e4b7,stroke:#333
    style OL fill:#c3e6cb,stroke:#333
    style NS fill:#f5c6cb,stroke:#333
```

## Fluxo de uma requisição

1. Cliente envia `POST /chat` com `{ "message": "...", "session_id": "abc" }`
2. `agent-service` monta o histórico da sessão e chama o LLM Gateway
3. `llm-gateway` (LiteLLM) roteia para Ollama com o modelo configurado
4. Ollama retorna a completion; se houver `tool_calls`, o agent executa a ferramenta localmente e reitera
5. Resposta final é devolvida ao cliente e o histórico é atualizado em memória

## Protocolos

| Origem | Destino | Protocolo |
|--------|---------|-----------|
| cliente | agent-service | REST/HTTP |
| agent-service | llm-gateway | REST/HTTP (OpenAI-compatible) |
| llm-gateway | Ollama | REST/HTTP |
| agent-service | name-server | REST/HTTP (Eureka heartbeat) |
```

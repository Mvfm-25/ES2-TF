# Status ES2 Tf.
[25-05-2026] [mvfm]

---

## O que está pronto

| Serviço | Estado | Observação |
|---------|--------|------------|
| `name-server` | Funcional | Eureka rodando na porta 8761 |
| `llm-gateway` | Funcional | LiteLLM + Ollama, porta 4000 |
| `agent-service` | Funcional | Ciclo agêntico básico com ferramenta de calculadora |
| `api-gateway` | Esqueleto | Roteamento e circuit breaker configurados; falta Redis para rate limiter |

---

## O que falta

### Entrega 2 — Infraestrutura (próximo passo imediato)

O `api-gateway` já tem roteamento e circuit breaker configurados, mas o `RequestRateLimiter`
exige um **Redis** como backend de contagem. Antes de subir o gateway, é preciso:

1. Instalar e subir um Redis local (`redis-server` ou via `winget install Redis.Redis`)
2. Adicionar a dependência `spring-boot-starter-data-redis-reactive` no `pom.xml`
3. Configurar `spring.data.redis.host/port` no `application.yml`

---

### Entrega 3 — Memória e RAG

**memory-service** ainda não existe. É o próximo serviço a criar:

- Spring Boot + Redis (memória de curto prazo — histórico da sessão ativa)
- Spring Boot + PostgreSQL (memória de longo prazo — histórico persistido entre sessões)
- O `agent-service` hoje guarda histórico **em memória local** (`session_store` em `main.py`);
  isso precisa migrar para chamadas REST ao `memory-service`

**retrieval-service** também não existe:

- FastAPI + ChromaDB (ou Qdrant)
- Precisa de um pipeline de ingestão: upload de documento → chunking → embedding via Ollama → indexação
- O `agent-service` ganha uma nova ferramenta (`search_documents`) que chama este serviço

---

### Entrega 4 — Mensageria

Ainda não feito, requer :

1. `agent-service` publica evento de telemetria no RabbitMQ após cada chamada ao LLM
   (tempo de resposta, modelo, ferramenta usada) — sem bloquear a resposta ao cliente
2. Ingestão de documentos no `retrieval-service` via fila, em vez de chamada REST síncrona

---

### Entrega 5 — Containerização

Sem dockerfile por em quanto, precisa : 

1. `Dockerfile` para `name-server` e `api-gateway` (imagem `eclipse-temurin:21-jre`)
2. `Dockerfile` para `agent-service` (imagem `python:3.11-slim`)
3. `llm-gateway` usa a imagem oficial `ghcr.io/berriai/litellm`
4. `docker-compose.yaml` unificando tudo com healthchecks e dependências explícitas

---

### Entrega 6 — Observabilidade

Nada feito, mas é bem direto : 

- Adicionar o SDK do **OpenTelemetry** no `agent-service` (Python) e nos serviços Spring Boot
- Subir o **Jaeger** (all-in-one) no Compose e apontar o exporter OTLP para ele
- O ponto mais crítico a rastrear é o span completo de uma requisição: gateway → agent → llm-gateway → Ollama

---

### Entregas 7 e 8 — Kubernetes e Entrega Final

Dependem de tudo anterior estar estável no Docker Compose. Não precisaria de nada mais além das entregas anteriores (lol).
---



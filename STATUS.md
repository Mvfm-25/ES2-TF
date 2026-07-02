# Status ES2 Tf.
[25-05-2026] [mvfm] — atualizado em [02-07-2026]

---

## O que está pronto

| Serviço | Estado | Observação |
|---------|--------|------------|
| `name-server` | Funcional | Eureka rodando na porta 8761 |
| `llm-gateway` | Funcional | LiteLLM + Ollama (`llama3.2`), porta 4000 |
| `agent-service` | Funcional | Ciclo agêntico com calculadora; bugs do `ERROS.md` (calculadora + loop infinito) corrigidos e verificados end-to-end |
| `api-gateway` | Funcional | Porta 8080; roteamento via Eureka, circuit breaker e **rate limiter Redis** ativos e validados (429 ao estourar o burst) |

---

## Ambiente (build/run validado em [28-06-2026])

- **Java**: o `java` no PATH é Java 8 e não roda os JARs; usar o JDK 21 em `C:\Program Files\Java\jdk-21.0.11` por caminho absoluto (definir `JAVA_HOME` não basta).
- **Python**: o default 3.13 não compila `pydantic==2.7.4`; usar **Python 3.12** (`py -3.12`). Há um venv por serviço: `agent-service/.venv` e `llm-gateway/.venv`.
- **Ollama**: instalado em `%LOCALAPPDATA%\Programs\Ollama\ollama.exe` (servidor sobe sozinho na 11434); modelo `llama3.2` baixado.
- **Redis**: provido pelo **Memurai Developer 4.1.2** (winget `Memurai.MemuraiDeveloper`, compatível com Redis 7.2.5), instalado como serviço do Windows na porta 6379. A instalação exige elevação (UAC); `winget` sem admin falha com 1603. CLI de teste: `C:\Program Files\Memurai\memurai-cli.exe ping`.

---

## O que falta

### ~~Entrega 2 — Infraestrutura~~ — CONCLUÍDA [02-07-2026]

O `api-gateway` sobe na porta 8080 com roteamento via Eureka, circuit breaker (Resilience4j)
e rate limiter distribuído (token bucket no Redis). O que foi feito:

1. Redis provisionado via **Memurai** (ver seção Ambiente) — porta 6379
2. Dependência `spring-boot-starter-data-redis-reactive` adicionada ao `pom.xml`
3. `spring.data.redis.host/port` configurados no `application.yml` (via env `REDIS_HOST`/`REDIS_PORT`)
4. Criado o bean **`ipKeyResolver`** (`RateLimiterConfig.java`) e referenciado em `key-resolver: "#{@ipKeyResolver}"`.
   Sem um `KeyResolver`, o gateway cai no `PrincipalNameKeyResolver` e responde 403 a tudo (não estava documentado antes).
5. Reordenados os filtros: **`RequestRateLimiter` antes do `CircuitBreaker`**, para rejeitar excesso de carga (429)
   sem gastar chamada do CB nem alcançar o downstream.

Validado end-to-end: `redis: UP` no `/actuator/health`; 60 requisições simultâneas a `/api/agent/**`
→ 20 passam (`burstCapacity`) e 40 retornam **429** (`replenishRate: 10`, `burstCapacity: 20`).

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



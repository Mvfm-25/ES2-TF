# Plataforma de Agentes Conversacionais — Entrega 1

## Pré-requisitos

- Java 21 + Maven 3.9+
- Python 3.11+
- [Ollama](https://ollama.ai) instalado e no PATH

## Startup (ordem obrigatória)

### 1. Ollama + modelo
```powershell
ollama pull llama3.2
ollama serve
```

### 2. name-server (Eureka — porta 8761)
```powershell
cd name-server
mvn spring-boot:run
# Dashboard: http://localhost:8761
```

### 3. llm-gateway (LiteLLM — porta 4000)
```powershell
cd llm-gateway
pip install -r requirements.txt
.\start.ps1
# Docs: http://localhost:4000/docs
```

### 4. agent-service (FastAPI — porta 8000)
```powershell
cd agent-service
pip install -r requirements.txt
python main.py
# Docs: http://localhost:8000/docs
```

## Testando

```powershell
# Chat simples
Invoke-RestMethod -Method Post -Uri http://localhost:8000/chat `
  -ContentType "application/json" `
  -Body '{"message": "Quanto é 15 * 47?", "session_id": "teste"}'

# Verificar serviços registrados no Eureka
Invoke-RestMethod http://localhost:8761/eureka/apps
```

## Estrutura

```
es/
├── name-server/      Java 21 + Spring Boot 3.3 + Eureka Server
├── llm-gateway/      Python 3.11 + LiteLLM (proxy p/ Ollama)
├── agent-service/    Python 3.11 + FastAPI  (ciclo agêntico)
└── diagrama.md       Arquitetura Mermaid
```

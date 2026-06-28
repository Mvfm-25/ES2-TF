# ERROS PRESENTES
## [26-06-2026] [mvfm]
---
### Lembrete
- Tais erros são simplesmente os que foram encontrados, isso não significa que são os únicos existentes. 
- Tendo um desenvolvimento extremamente go horse-like, é bem provável que eu tenha perdido muita coisa.
---
1. ~~Calculadora presente simplesmente se recusando a funcionar corretamente,=.~~
2. ~~Quebrado o ciclo correto de ação -> observação, causando um erro de loop infinito.~~

---
## Resolvidos [28-06-2026]

1. **Calculadora.** `execute_tool` usava `vars(__builtins__)`; em módulo importado `__builtins__`
   é um dict (não módulo), então `vars()` lançava `TypeError` e a ferramenta sempre retornava erro.
   Corrigido para `{k: getattr(builtins, k) for k in _ALLOWED_BUILTINS}` em `agent.py`.
2. **Loop infinito ação→observação.** O ciclo era um `while True` sem limite de passos. Trocado por
   `for step in range(MAX_STEPS)` (default 5, via env `AGENT_MAX_STEPS`); no último passo força
   `tool_choice="none"` para obrigar uma resposta em texto.
   Obs.: o `llama3.2` tende a rechamar a ferramenta mesmo após receber o resultado correto — o limite
   de passos é o que garante o término. Verificado end-to-end (chat "15 * 47" → "705", HTTP 200).

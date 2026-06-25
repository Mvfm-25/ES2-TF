import httpx
import os
from typing import Any

LLM_GATEWAY_URL = os.getenv("LLM_GATEWAY_URL", "http://localhost:4000")
LLM_API_KEY = os.getenv("LLM_GATEWAY_API_KEY", "sk-local-dev")
LLM_MODEL = os.getenv("LLM_MODEL", "local")

TOOLS: dict[str, dict] = {
    "calculator": {
        "description": "Avalia expressões matemáticas simples.",
        "schema": {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Avalia uma expressão matemática e retorna o resultado numérico.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Expressão matemática a ser avaliada, ex: '2 + 2 * 3'"
                        }
                    },
                    "required": ["expression"]
                }
            }
        }
    }
}


def execute_tool(name: str, args: dict[str, Any]) -> str:
    if name == "calculator":
        try:
            # eval restrito a operações numéricas
            allowed = {k: v for k, v in vars(__builtins__).items()
                       if k in ("abs", "round", "min", "max", "sum", "pow")}
            result = eval(args["expression"], {"__builtins__": allowed})
            return str(result)
        except Exception as e:
            return f"Erro ao calcular: {e}"
    return f"Ferramenta '{name}' não encontrada."


async def run_agent(user_message: str, history: list[dict]) -> tuple[str, list[dict]]:
    """
    Ciclo agêntico: raciocínio → ação → observação.
    Retorna a resposta final e o histórico atualizado.
    """
    messages = history + [{"role": "user", "content": user_message}]
    tool_schemas = [t["schema"] for t in TOOLS.values()]

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        while True:
            payload = {
                "model": LLM_MODEL,
                "messages": messages,
                "tools": tool_schemas,
                "tool_choice": "auto",
            }

            response = await client.post(
                f"{LLM_GATEWAY_URL}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

            choice = data["choices"][0]
            message = choice["message"]
            messages.append(message)

            # Sem tool_calls → resposta final
            if not message.get("tool_calls"):
                final_text = message.get("content", "")
                return final_text, messages

            # Executa cada ferramenta solicitada (ação → observação)
            for tool_call in message["tool_calls"]:
                import json
                fn_name = tool_call["function"]["name"]
                fn_args = json.loads(tool_call["function"]["arguments"])
                observation = execute_tool(fn_name, fn_args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": observation,
                })

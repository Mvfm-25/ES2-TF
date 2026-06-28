import builtins
import json
import httpx
import os
from typing import Any

LLM_GATEWAY_URL = os.getenv("LLM_GATEWAY_URL", "http://localhost:4000")
LLM_API_KEY = os.getenv("LLM_GATEWAY_API_KEY", "sk-local-dev")
LLM_MODEL = os.getenv("LLM_MODEL", "local")

MAX_STEPS = int(os.getenv("AGENT_MAX_STEPS", "5"))

_ALLOWED_BUILTINS = ("abs", "round", "min", "max", "sum", "pow")

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
            allowed = {k: getattr(builtins, k) for k in _ALLOWED_BUILTINS}
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
        for step in range(MAX_STEPS):
            final_step = step == MAX_STEPS - 1
            payload = {
                "model": LLM_MODEL,
                "messages": messages,
                "tools": tool_schemas,
                "tool_choice": "none" if final_step else "auto",
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

            if not message.get("tool_calls"):
                final_text = message.get("content", "")
                return final_text, messages

            for tool_call in message["tool_calls"]:
                fn_name = tool_call["function"]["name"]
                fn_args = json.loads(tool_call["function"]["arguments"])
                observation = execute_tool(fn_name, fn_args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": observation,
                })

    final_text = messages[-1].get("content", "") if messages else ""
    return final_text, messages

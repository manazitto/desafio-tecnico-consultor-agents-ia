"""Interface Chainlit para o Banco Agil."""
import chainlit as cl
from langchain_core.messages import AIMessage, HumanMessage

from banco_agil.config import GEMINI_API_KEY, LLM_MODEL
from banco_agil.core.graph import AgentState, create_runnable


@cl.on_chat_start
async def on_chat_start():
    """Inicializa a sessao do chat."""
    graph = create_runnable(api_key=GEMINI_API_KEY, model=LLM_MODEL)
    state: AgentState = {
        "messages": [],
        "current_agent": "triage",
        "client_data": {},
        "conversation_ended": False,
    }
    cl.user_session.set("graph", graph)
    cl.user_session.set("state", state)

    await cl.Message(
        content="Bem-vindo ao **Banco Agil**! Sou seu atendente virtual. Como posso ajuda-lo hoje?"
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Processa mensagem do usuario."""
    graph = cl.user_session.get("graph")
    state = cl.user_session.get("state")

    if state.get("conversation_ended"):
        await cl.Message(content="Atendimento encerrado. Obrigado por utilizar o Banco Agil!").send()
        return

    msg = cl.Message(content="")
    await msg.send()

    try:
        state["messages"].append(HumanMessage(content=message.content))
        result = graph.invoke(state)

        # Atualizar state da sessao
        cl.user_session.set("state", result)

        # Extrair ultima AIMessage
        ai_response = ""
        for m in reversed(result["messages"]):
            if isinstance(m, AIMessage) and m.content and not getattr(m, "tool_calls", None):
                ai_response = m.content
                break

        # Atualizar client_data se autenticacao ocorreu
        for m in result["messages"]:
            if hasattr(m, "content") and isinstance(m.content, str) and '"authenticated": true' in m.content.lower():
                import json
                try:
                    data = json.loads(m.content)
                    if data.get("authenticated") and "cliente" in data:
                        cliente = data["cliente"]
                        result["client_data"] = {
                            "nome": cliente.get("nome", ""),
                            "cpf": cliente.get("cpf", ""),
                            "score": cliente.get("score", 0),
                            "limite": cliente.get("limite", 0),
                        }
                        cl.user_session.set("state", result)
                except (json.JSONDecodeError, TypeError):
                    pass

        msg.content = ai_response or "Desculpe, tive um problema ao processar sua solicitacao."
        await msg.update()
    except Exception:
        msg.content = "Desculpe, ocorreu um erro inesperado. Por favor, tente novamente."
        await msg.update()

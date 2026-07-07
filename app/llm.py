"""向后兼容层，委托给 ModelRouter。"""
from app.router import model_router


def chat(messages, tools=None, temperature=0.7, model=None):
    provider = model_router.get_provider(model_router.resolve_model_id(model))
    return provider.chat(messages, tools=tools, temperature=temperature)


def chat_stream(messages, tools=None, temperature=0.7, model=None):
    provider = model_router.get_provider(model_router.resolve_model_id(model))
    yield from provider.chat_stream(messages, tools=tools, temperature=temperature)


def ask_llm(prompt: str, model=None) -> str:
    msg = chat([
        {"role": "system", "content": "你是一个智能助手"},
        {"role": "user", "content": prompt},
    ], model=model)
    return msg.get("content", "")

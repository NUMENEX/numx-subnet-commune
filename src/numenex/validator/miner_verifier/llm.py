from langchain_groq import ChatGroq
import os


def get_llm(
    model: str,
    api_key: str,
    temperature: int,
    max_tokens: int,
    timeout: int,
    max_retries: int,
) -> ChatGroq:
    os.environ["GROQ_API_KEY"] = api_key
    return ChatGroq(
        model=model,
        temperature=int(temperature),
        max_tokens=int(max_tokens) if max_tokens != "None" else None,
        timeout=int(timeout) if timeout != "None" else None,
        max_retries=int(max_retries) if max_retries != "None" else None,
    )

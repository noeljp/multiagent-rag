from openai import OpenAI
import tiktoken
import time

client = OpenAI()

def run_chat_completion(system_prompt: str, user_prompt: str, model: str = "gpt-4", temperature: float = 0.2, max_tokens: int = 1000):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    start = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    end = time.time()
    print(f"[LLM CALL] Model: {model} | Tokens: ~{count_tokens(messages, model)} | Time: {end - start:.2f}s")
    return response.choices[0].message.content

def count_tokens(messages, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    total_tokens = 0
    for msg in messages:
        total_tokens += 4  # per message overhead
        total_tokens += len(encoding.encode(msg["content"]))
    total_tokens += 2  # priming
    return total_tokens
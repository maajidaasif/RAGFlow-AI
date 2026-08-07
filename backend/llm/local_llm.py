from llama_cpp import Llama

llm = Llama(
    model_path="models/qwen2.5-3b-instruct-q4_k_m.gguf",
    n_ctx=4096,
    n_threads=8,
    n_gpu_layers=0,
    chat_format="chatml",
    verbose=False
)


def ask_llm(question, context, max_tokens=80):

    response = llm.create_chat_completion(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert AI Research Paper Analysis Assistant.\n"
                    "Answer ONLY using the supplied research paper context.\n"
                    "Never use outside knowledge.\n"
                    "Never invent paper names, authors, datasets, models, methods, or results.\n"
                    "If information is unavailable, reply with 'Not Available'.\n"
                    "Write in professional academic English.\n"
                    "Avoid repeating the same information.\n"
                    "Return clear, well-structured Markdown.\n"
                    "Return only the final answer."
                )
            },
            {
                "role": "user",
                "content": f"""
Research Paper Context

{context}

Task

{question}
"""
            }
        ],
        temperature=0.1,
        top_p=0.9,
        repeat_penalty=1.20,
        max_tokens=max_tokens
    )

    return response["choices"][0]["message"]["content"].strip()
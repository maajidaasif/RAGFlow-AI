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
                    "You are an AI Research Paper Information Extraction Assistant.\n"
                    "Use ONLY the supplied research paper context.\n"
                    "Never use outside knowledge.\n"
                    "Never invent paper names, authors, datasets, models or methods.\n"
                    "If something is not present in the uploaded papers, do not mention it.\n"
                    "Do not guess.\n"
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
        temperature=0.0,
        top_p=0.8,
        repeat_penalty=1.15,
        max_tokens=max_tokens
    )

    return response["choices"][0]["message"]["content"].strip()
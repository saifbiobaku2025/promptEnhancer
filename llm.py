import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "gemini")

print("PROVIDER:", os.getenv("LLM_PROVIDER"))
print("KEY:", os.getenv("GEMINI_API_KEY", "NOT FOUND"))

# ── Client factory ─────────────────────────────────────────────────────────
def get_client() -> tuple[OpenAI, str]:
    """Returns (client, model_name) based on LLM_PROVIDER env var."""
    if PROVIDER == "groq":
        return OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        ), os.getenv("GROQ_MODEL", "llama3-70b-8192")

    elif PROVIDER == "openrouter":
        return OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        ), os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct")

    elif PROVIDER == "gemini":
        return OpenAI(
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        ), os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    raise ValueError(f"Unknown provider: {PROVIDER}")


# ── Meta-prompt template ────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert prompt engineer. Your job is to transform vague user prompts into highly optimized instructions for large language models.

For each input, you MUST:
1. Detect the underlying INTENT (code, writing, analysis, creative, etc.)
2. Add specific CONTEXT (domain, audience, constraints)
3. Include 2 CONCRETE EXAMPLES (few-shot style) relevant to the task
4. Add CHAIN-OF-THOUGHT instruction: "Think step by step."
5. Specify OUTPUT FORMAT (e.g., markdown, JSON, bullet list, prose)
6. Include 2–3 EDGE CASES or constraints to handle
7. Set a QUALITY BAR ("Be precise, production-ready, under 200 words")

Output format:
---INTENT: [detected intent in 3 words]
---ENHANCED PROMPT:
[The full optimized prompt here]

Be concise but complete. The enhanced prompt should be self-contained."""


def enhance_prompt(
    user_prompt: str,
    intent_override: str = "Auto-detect",
    temperature: float = 0.7,
    seed: int = 0
) -> dict:
    """
    Calls LLM to enhance a vague prompt.
    Returns {"intent": str, "enhanced": str, "tokens": int}
    """
    client, model = get_client()

    # Inject intent override if user specified one
    user_message = user_prompt
    if intent_override != "Auto-detect":
        user_message = f"[Intent hint: {intent_override}]\n\n{user_prompt}"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=temperature,
        max_tokens=1024,
        seed=seed if seed > 0 else None,  # seed=None gives fresh output
    )

    raw = response.choices[0].message.content.strip()

    # Parse intent from output
    intent = "unknown"
    enhanced = raw
    if "---INTENT:" in raw:
        lines = raw.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("---INTENT:"):
                intent = line.replace("---INTENT:", "").strip()
            if line.startswith("---ENHANCED PROMPT:"):
                enhanced = "\n".join(lines[i+1:]).strip()

    return {
        "intent": intent,
        "enhanced": enhanced,
        "tokens": response.usage.total_tokens
    }
# src/main.py

import os
from datetime import datetime

import openai
from dotenv import load_dotenv

load_dotenv()

# Konfiguracja dla Azure
openai.api_type = "azure"
openai.api_base = "https://openai-bost593.openai.azure.com"
openai.api_version = "2024-12-01-preview"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")

DEPLOYMENT_NAME = "gpt-4o"

prompts = [
    "Opisz krótko historię Polski.",
    "Policz pierwiastek kwadratowy z 987654321.",
    "Podaj przepisy na 3 szybkie obiady z ziemniaków."
]


def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """
    Oblicz koszt zużycia tokenów na podstawie cennika.
    """
    return round((input_tokens * 0.01 + output_tokens * 0.03) / 1000, 6)


def log_prompts(prompts: list[str], log_path: str) -> None:
    """
    Loguj dane o zapytaniach do pliku markdown.
    """
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    try:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"# GPT-4o – raport użycia ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n\n")
            most_efficient = {"prompt": "", "cost_per_token": float("inf")}

            for i, prompt in enumerate(prompts, 1):
                response = openai.ChatCompletion.create(
                    engine=DEPLOYMENT_NAME,
                    messages=[{"role": "user", "content": prompt}]
                )
                usage = response["usage"]
                input_toks = usage["prompt_tokens"]
                output_toks = usage["completion_tokens"]
                total_toks = usage["total_tokens"]
                cost = calculate_cost(input_toks, output_toks)
                cost_per_token = cost / total_toks if total_toks else 0

                f.write(f"## Prompt {i}\n")
                f.write(f"**Treść:** {prompt}\n")
                f.write(f"- Tokeny wejściowe: {input_toks}\n")
                f.write(f"- Tokeny wyjściowe: {output_toks}\n")
                f.write(f"- Suma tokenów: {total_toks}\n")
                f.write(f"- Koszt: ${cost:.6f}\n")
                f.write(f"- Koszt/token: ${cost_per_token:.6f}\n\n")

                if cost_per_token < most_efficient["cost_per_token"]:
                    most_efficient = {"prompt": prompt, "cost_per_token": cost_per_token}

            f.write("### Najbardziej efektywny prompt:\n")
            f.write(f"**Treść:** {most_efficient['prompt']}\n")
            f.write(f"**Koszt/token:** ${most_efficient['cost_per_token']:.6f}\n")

    except Exception as e:
        print(f"Błąd przy zapisie logów: {e}")


if __name__ == "__main__":
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs", "usage.md")
    log_prompts(prompts, log_path)
    print(f"Gotowe! Zobacz log w: {log_path}")

import os
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime

import openai
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate

# Ścieżki
BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"
LOGS_DIR = BASE_DIR / "logs"
RESULTS_DIR = BASE_DIR / "results"
PROMPTS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "app.log"),
        logging.StreamHandler()
    ]
)

# OpenAI setup
load_dotenv()
openai.api_type = "azure"
openai.api_base = "https://openai-bost593.openai.azure.com"
openai.api_version = "2024-12-01-preview"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = "gpt-4o"

def create_best_prompt():
    prompt = PromptTemplate.from_template(
        "Jesteś quiz-botem. Zadaj pytanie z czterema odpowiedziami (A, B, C, D). Oznacz prawidłową."
    )
    with open(PROMPTS_DIR / "best.txt", "w", encoding="utf-8") as f:
        f.write(prompt.template)
    logging.info("Zapisano prompt quiz-bota.")

def suggest_peer_improvement():
    suggestion = "Dodaj tło historyczne do pytania, np. kontekst epoki."
    with open(PROMPTS_DIR / "suggestion_for_peer.txt", "w", encoding="utf-8") as f:
        f.write(suggestion)
    logging.info("Zapisano sugestię dla promptu kolegi.")

def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    return round((input_tokens * 0.01 + output_tokens * 0.03) / 1000, 6)

def log_prompts(prompts: list[str]):
    usage_list = []
    for prompt in prompts:
        try:
            response = openai.ChatCompletion.create(
                engine=DEPLOYMENT_NAME,
                messages=[{"role": "user", "content": prompt}]
            )
            usage = response["usage"]
            input_toks = usage["prompt_tokens"]
            output_toks = usage["completion_tokens"]
            total_toks = usage["total_tokens"]
            cost = calculate_cost(input_toks, output_toks)

            usage_entry = {
                "prompt": prompt,
                "prompt_tokens": input_toks,
                "completion_tokens": output_toks,
                "total_tokens": total_toks,
                "cost": cost,
                "timestamp": datetime.now().isoformat()
            }
            usage_list.append(usage_entry)
            logging.info(f"Zalogowano prompt: {prompt}")
        except Exception as e:
            logging.error(f"Błąd zapytania: {e}")

    with open(LOGS_DIR / "usage.json", "w", encoding="utf-8") as f:
        json.dump(usage_list, f, indent=2, ensure_ascii=False)

def run_quiz_game():
    questions = [
        {
            "question": "Jakie miasto jest stolicą Polski?",
            "options": ["A) Kraków", "B) Gdańsk", "C) Warszawa", "D) Łódź"],
            "answer": "C"
        },
        {
            "question": "Co to jest 15 * 3?",
            "options": ["A) 35", "B) 40", "C) 45", "D) 50"],
            "answer": "C"
        },
        {
            "question": "Który pierwiastek ma symbol 'O'?",
            "options": ["A) Osm", "B) Tlen", "C) Ołów", "D) Oran"],
            "answer": "B"
        }
    ]

    prize = 1000
    game_log = {
        "start_time": datetime.now().isoformat(),
        "answers": [],
        "final_prize": 0
    }

    print("\n🎮 Witaj w grze 'Milionerzy'!")

    for i, q in enumerate(questions, 1):
        print(f"\nPytanie {i}: {q['question']}")
        for option in q["options"]:
            print(option)
        user_answer = input("Wybierz (A/B/C/D): ").strip().upper()
        correct = user_answer == q["answer"]
        game_log["answers"].append({
            "question": q["question"],
            "user_answer": user_answer,
            "correct": correct,
            "prize_before": prize
        })

        if correct:
            print("Poprawna odpowiedź :)!")
            prize *= 2
        else:
            print(f"Błędna odpowiedź :(. Poprawna to: {q['answer']}")
            prize = 0
            break

    game_log["final_prize"] = prize
    game_log["end_time"] = datetime.now().isoformat()

    with open(RESULTS_DIR / "game_results.json", "w", encoding="utf-8") as f:
        json.dump(game_log, f, indent=2, ensure_ascii=False)

    logging.info(f"Gra zakończona. Wygrana: {prize} zł.")
    print(f"\n💰 Gra zakończona. Twoja wygrana to: {prize} zł.")

def main():
    parser = argparse.ArgumentParser(description="Quiz-bot CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("generate_prompt", help="Zapisz prompt quiz-bota")
    subparsers.add_parser("suggest_peer", help="Zapisz sugestię dla promptu kolegi")
    subparsers.add_parser("play_game", help="Zagraj w quiz w stylu Milionerzy")
    subparsers.add_parser("log", help="Zaloguj użycie promptów")

    args = parser.parse_args()

    if args.command == "generate_prompt":
        create_best_prompt()
    elif args.command == "suggest_peer":
        suggest_peer_improvement()
    elif args.command == "play_game":
        run_quiz_game()
    elif args.command == "log":
        prompts = [
            "Opisz krótko historię Polski.",
            "Policz pierwiastek kwadratowy z 987654321.",
            "Podaj przepisy na 3 szybkie obiady z ziemniaków."
        ]
        log_prompts(prompts)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

# 1. Zapisujemy prompt quiz-bota do /prompts/best.txt
# 2. Zostawiamy sugestię ulepszenia promptu kolegi do /prompts/suggestion_for_peer.txt
# 3. Tworzymy prostą grę quizową w Pythonie (command line) w pliku quiz_game.py

import os

# Tworzenie wymaganych folderów
os.makedirs("prompts", exist_ok=True)
os.makedirs("game", exist_ok=True)

# 1. Quiz-bot prompt (do użycia np. z GPT lub jako koncepcja)
quiz_bot_prompt = """\
Jesteś quiz-botem. Zadaj użytkownikowi jedno pytanie quizowe z czterema możliwymi odpowiedziami (A, B, C, D)
z zakresu wiedzy ogólnej. Poczekaj na odpowiedź użytkownika. Następnie powiedz, czy odpowiedź była poprawna,
podaj prawidłową odpowiedź i krótkie wyjaśnienie. Odpowiadaj po polsku i w przyjaznym tonie.
"""

with open("prompts/best.txt", "w", encoding="utf-8") as f:
    f.write(quiz_bot_prompt)

# 2. Sugestia
peer_prompt_suggestion = """\
Warto byłoby dodać informację, że quiz-bot ma najpierw poczekać na odpowiedź użytkownika,
a dopiero potem ją ocenić. Dzięki temu rozmowa będzie bardziej interaktywna i realistyczna.
"""

with open("prompts/suggestion_for_peer.txt", "w", encoding="utf-8") as f:
    f.write(peer_prompt_suggestion)

# 3. Gra w Pythonie (command line quiz)
quiz_game_code = """\
# Prosta gra quizowa do terminala (Day 7 demo)
questions = [
    {
        "question": "Który pierwiastek ma symbol 'H'?",
        "options": ["A) Hel", "B) Wodór", "C) Wapń", "D) Tlen"],
        "answer": "B"
    },
    {
        "question": "Ile kontynentów ma Ziemia?",
        "options": ["A) 5", "B) 6", "C) 7", "D) 8"],
        "answer": "C"
    },
    {
        "question": "Kto napisał 'Lalkę'?",
        "options": ["A) Henryk Sienkiewicz", "B) Adam Mickiewicz", "C) Eliza Orzeszkowa", "D) Bolesław Prus"],
        "answer": "D"
    }
]

score = 0

for q in questions:
    print("\\n" + q["question"])
    for option in q["options"]:
        print(option)
    user_answer = input("Twoja odpowiedź (A/B/C/D): ").strip().upper()
    if user_answer == q["answer"]:
        print("Poprawna odpowiedź!")
        score += 1
    else:
        print(f"Błędna odpowiedź. Poprawna to: {q['answer']}")

print(f"\\nTwój wynik końcowy: {score}/{len(questions)}")
"""

with open("game/quiz_game.py", "w", encoding="utf-8") as f:
    f.write(quiz_game_code)

# Spakuj projekt do pobrania
import shutil
shutil.make_archive("/mnt/data/quiz_project_day7_clean", 'zip', '.')

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
    print("\n" + q["question"])
    for option in q["options"]:
        print(option)
    user_answer = input("Twoja odpowiedź (A/B/C/D): ").strip().upper()
    if user_answer == q["answer"]:
        print("Poprawna odpowiedź!")
        score += 1
    else:
        print(f"Błędna odpowiedź. Poprawna to: {q['answer']}")

print(f"\nTwój wynik końcowy: {score}/{len(questions)}")

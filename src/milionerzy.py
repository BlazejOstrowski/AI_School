import os
import json
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from pathlib import Path
import random

from PIL import Image, ImageTk
import openai
from dotenv import load_dotenv

# Paths
BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Load API
load_dotenv()
openai.api_type = "azure"
openai.api_base = "https://openai-bost593.openai.azure.com"
openai.api_version = "2024-12-01-preview"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = "gpt-4o"

# Rewards
REWARDS = [500, 1000, 2000, 5000]
GUARANTEED_LEVEL = 1


def fetch_questions():
    prompt = (
        "Create 4 quiz questions in the style of 'Who Wants to Be a Millionaire'. "
        "Each question should have 4 options A-D, and mark the correct one with 'answer'. "
        "Return a JSON list: "
        "[{'question': '...', 'options': ['A) ...', 'B) ...', 'C) ...', 'D) ...'], 'answer': 'A'}]"
    )
    try:
        response = openai.ChatCompletion.create(
            engine=DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response["choices"][0]["message"]["content"]

        import re
        clean_content = re.sub(r"^```json|```$", "", content, flags=re.MULTILINE).strip()
        return json.loads(clean_content)
    except Exception as e:
        print("Error fetching questions:", e)
        return []


class MillionaireGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Who Wants to Be a Millionaire?")
        self.questions = fetch_questions()
        self.index = 0
        self.reward = 0
        self.results = []
        self.used_5050 = False

        # Background
        self.canvas = tk.Canvas(self.root, width=800, height=600)
        self.canvas.pack(fill="both", expand=True)

        bg_path = BASE_DIR / "milionerzy_bg.jpg"
        if bg_path.exists():
            self.bg_image = Image.open(bg_path).resize((800, 600))
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # Score label
        self.score_label = tk.Label(self.root, text="Score: 0 zł", font=("Arial", 12, "bold"), bg="white")
        self.score_label.place(x=50, y=10)

        # Question label
        self.question_label = tk.Label(self.root, text="", font=("Arial", 14), wraplength=700, bg="white")
        self.question_label.place(x=50, y=40)

        # Answer buttons
        self.buttons = []
        for i in range(4):
            btn = tk.Button(self.root, text="", font=("Arial", 12), width=50,
                            command=lambda i=i: self.check_answer(i))
            btn.place(x=150, y=120 + i * 60)
            self.buttons.append(btn)

        # 50:50 button
        self.btn_5050 = tk.Button(self.root, text="50:50", font=("Arial", 10), command=self.use_5050)
        self.btn_5050.place(x=700, y=10)

        # Quit button
        self.btn_quit = tk.Button(self.root, text="Quit and take reward", font=("Arial", 10),
                                  command=self.quit_game)
        self.btn_quit.place(x=550, y=10)

        self.show_question()

    def show_question(self):
        if self.index < len(self.questions):
            self.btn_5050.config(state="normal" if not self.used_5050 else "disabled")
            q = self.questions[self.index]
            self.question_label.config(text=f"{self.index + 1}. {q['question']}")
            for i in range(4):
                self.buttons[i].config(text=q['options'][i], state="normal")
            self.score_label.config(text=f"Score: {self.reward} zł")
        else:
            self.end_game(won=True)

    def check_answer(self, idx):
        question = self.questions[self.index]
        selected = question["options"][idx][0]
        correct = question["answer"]
        is_correct = selected == correct

        self.results.append({
            "question": question["question"],
            "selected": selected,
            "correct": correct,
            "is_correct": is_correct,
            "amount": REWARDS[self.index]
        })

        if is_correct:
            self.reward = REWARDS[self.index]
            self.index += 1
            self.show_question()
        else:
            self.end_game(won=False)

    def use_5050(self):
        if self.used_5050:
            return
        question = self.questions[self.index]
        correct = question["answer"]
        wrong_indices = [i for i in range(4) if question["options"][i][0] != correct]
        to_disable = random.sample(wrong_indices, 2)
        for i in to_disable:
            self.buttons[i].config(state="disabled")
        self.used_5050 = True
        self.btn_5050.config(state="disabled")

    def quit_game(self):
        self.end_game(won=True)

    def end_game(self, won):
        if not won and self.index > GUARANTEED_LEVEL:
            self.reward = REWARDS[GUARANTEED_LEVEL]

        result_data = {
            "timestamp": datetime.now().isoformat(),
            "answers": self.results,
            "final_reward": self.reward
        }

        result_path = RESULTS_DIR / f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=2, ensure_ascii=False)

        msg = f" You won {self.reward} zł!" if won else f"Game over. You won: {self.reward} zł"
        messagebox.showinfo("Result", msg)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = MillionaireGame(root)
    root.mainloop()

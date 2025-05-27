import os
import json
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from pathlib import Path
import random
import logging

from PIL import Image, ImageTk
import openai
from dotenv import load_dotenv

# Logger setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("game.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
        logger.info("Sending request to OpenAI for quiz questions.")
        response = openai.ChatCompletion.create(
            engine=DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response["choices"][0]["message"]["content"]
        logger.info("Received response from OpenAI.")

        import re
        clean_content = re.sub(r"^```json|```$", "", content, flags=re.MULTILINE).strip()
        questions = json.loads(clean_content)
        logger.info(f"Parsed {len(questions)} questions successfully.")
        return questions
    except Exception as e:
        logger.error(f"Error fetching questions: {e}")
        return []


class MillionaireGame:
    def __init__(self, root):
        logger.info("Initializing game interface.")
        self.root = root
        self.root.title("Who Wants to Be a Millionaire?")
        self.questions = fetch_questions()
        self.index = 0
        self.reward = 0
        self.results = []
        self.used_5050 = False

        self.canvas = tk.Canvas(self.root, width=800, height=600)
        self.canvas.pack(fill="both", expand=True)

        bg_path = BASE_DIR / "milionerzy_bg.jpg"
        if bg_path.exists():
            self.bg_image = Image.open(bg_path).resize((800, 600))
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
            logger.info("Background image loaded.")
        else:
            logger.warning("Background image not found.")

        self.score_label = tk.Label(self.root, text="Score: 0 zł", font=("Arial", 12, "bold"), bg="white")
        self.score_label.place(x=50, y=10)

        self.question_label = tk.Label(self.root, text="", font=("Arial", 14), wraplength=700, bg="white")
        self.question_label.place(x=50, y=40)

        self.buttons = []
        for i in range(4):
            btn = tk.Button(self.root, text="", font=("Arial", 12), width=50,
                            command=lambda i=i: self.check_answer(i))
            btn.place(x=150, y=120 + i * 60)
            self.buttons.append(btn)

        self.btn_5050 = tk.Button(self.root, text="50:50", font=("Arial", 10), command=self.use_5050)
        self.btn_5050.place(x=700, y=10)

        self.btn_quit = tk.Button(self.root, text="Quit and take reward", font=("Arial", 10),
                                  command=self.quit_game)
        self.btn_quit.place(x=550, y=10)

        self.show_question()

    def show_question(self):
        if self.index < len(self.questions):
            logger.info(f"Displaying question {self.index + 1}.")
            self.btn_5050.config(state="normal" if not self.used_5050 else "disabled")
            q = self.questions[self.index]
            self.question_label.config(text=f"{self.index + 1}. {q['question']}")
            for i in range(4):
                self.buttons[i].config(text=q['options'][i], state="normal")
            self.score_label.config(text=f"Score: {self.reward} zł")
        else:
            logger.info("All questions completed. Ending game.")
            self.end_game(won=True)

    def check_answer(self, idx):
        question = self.questions[self.index]
        selected = question["options"][idx][0]
        correct = question["answer"]
        is_correct = selected == correct

        logger.info(f"Question answered. Selected: {selected}, Correct: {correct}, Result: {'Correct' if is_correct else 'Incorrect'}")

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
            logger.warning("50:50 already used.")
            return
        question = self.questions[self.index]
        correct = question["answer"]
        wrong_indices = [i for i in range(4) if question["options"][i][0] != correct]
        to_disable = random.sample(wrong_indices, 2)
        for i in to_disable:
            self.buttons[i].config(state="disabled")
        self.used_5050 = True
        self.btn_5050.config(state="disabled")
        logger.info("50:50 lifeline used.")

    def quit_game(self):
        logger.info("Player quit the game.")
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
        try:
            with open(result_path, "w", encoding="utf-8") as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Result saved to {result_path}")
        except Exception as e:
            logger.error(f"Error saving result file: {e}")

        msg = f"You won {self.reward} zł!" if won else f"Game over. You won: {self.reward} zł"
        messagebox.showinfo("Result", msg)
        self.root.destroy()


if __name__ == "__main__":
    logger.info("Game started.")
    root = tk.Tk()
    root.geometry("800x600")
    app = MillionaireGame(root)
    root.mainloop()
    logger.info("Game ended.")

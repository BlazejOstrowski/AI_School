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

# Ścieżki
BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Wczytaj API
load_dotenv()
openai.api_type = "azure"
openai.api_base = "https://openai-bost593.openai.azure.com"
openai.api_version = "2024-12-01-preview"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = "gpt-4o"

# Nagrody
NAGRODY = [500, 1000, 2000, 5000]
PROG_GWARANTOWANY = 1


def pobierz_pytania():
    prompt = (
        "Stwórz 4 pytania quizowe w stylu Milionerzy. "
        "Każde pytanie ma mieć 4 odpowiedzi A-D i poprawną oznaczoną jako 'answer'. "
        "Zwróć listę JSON: "
        "[{'question': '...', 'options': ['A) ...', 'B) ...', 'C) ...', 'D) ...'], 'answer': 'A'}]"
    )
    try:
        response = openai.ChatCompletion.create(
            engine=DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        wynik = response["choices"][0]["message"]["content"]

        import re
        czysty = re.sub(r"^```json|```$", "", wynik, flags=re.MULTILINE).strip()
        return json.loads(czysty)
    except Exception as e:
        print("❌ Błąd pobierania pytań:", e)
        return []


class MilionerzyGra:
    def __init__(self, root):
        self.root = root
        self.root.title("Milionerzy")
        self.pytania = pobierz_pytania()
        self.nr = 0
        self.nagroda = 0
        self.wyniki = []
        self.uzyte_5050 = False

        # Tło
        self.canvas = tk.Canvas(self.root, width=800, height=600)
        self.canvas.pack(fill="both", expand=True)

        tlo_path = BASE_DIR / "milionerzy_bg.jpg"
        if tlo_path.exists():
            self.bg_image = Image.open(tlo_path).resize((800, 600))
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")

        # Punkty
        self.punkty_label = tk.Label(self.root, text="Punkty: 0 zł", font=("Arial", 12, "bold"), bg="white")
        self.punkty_label.place(x=50, y=10)

        # Pytanie
        self.pytanie_label = tk.Label(self.root, text="", font=("Arial", 14), wraplength=700, bg="white")
        self.pytanie_label.place(x=50, y=40)

        # Przyciski odpowiedzi
        self.przyciski = []
        for i in range(4):
            btn = tk.Button(self.root, text="", font=("Arial", 12), width=50,
                            command=lambda i=i: self.sprawdz_odpowiedz(i))
            btn.place(x=150, y=120 + i * 60)
            self.przyciski.append(btn)

        # Przycisk 50:50
        self.btn_5050 = tk.Button(self.root, text="50:50", font=("Arial", 10), command=self.uzyj_5050)
        self.btn_5050.place(x=700, y=10)

        # Przycisk rezygnacji
        self.btn_rezygnuj = tk.Button(self.root, text="Zrezygnuj i weź nagrodę", font=("Arial", 10),
                                      command=self.rezygnuj)
        self.btn_rezygnuj.place(x=550, y=10)

        self.pokaz_pytanie()

    def pokaz_pytanie(self):
        if self.nr < len(self.pytania):
            self.btn_5050.config(state="normal" if not self.uzyte_5050 else "disabled")
            p = self.pytania[self.nr]
            self.pytanie_label.config(text=f"{self.nr + 1}. {p['question']}")
            for i in range(4):
                self.przyciski[i].config(text=p['options'][i], state="normal")
            self.punkty_label.config(text=f"Punkty: {self.nagroda} zł")
        else:
            self.koniec(wygrana=True)

    def sprawdz_odpowiedz(self, idx):
        pyt = self.pytania[self.nr]
        wybor = pyt["options"][idx][0]
        poprawna = pyt["answer"]
        poprawnie = wybor == poprawna

        self.wyniki.append({
            "pytanie": pyt["question"],
            "odpowiedz": wybor,
            "poprawna": poprawna,
            "czy_poprawna": poprawnie,
            "kwota": NAGRODY[self.nr]
        })

        if poprawnie:
            self.nagroda = NAGRODY[self.nr]
            self.nr += 1
            self.pokaz_pytanie()
        else:
            self.koniec(wygrana=False)

    def uzyj_5050(self):
        if self.uzyte_5050:
            return
        pyt = self.pytania[self.nr]
        poprawna = pyt["answer"]
        indices = [i for i in range(4) if pyt["options"][i][0] != poprawna]
        do_usuniecia = random.sample(indices, 2)
        for i in do_usuniecia:
            self.przyciski[i].config(state="disabled")
        self.uzyte_5050 = True
        self.btn_5050.config(state="disabled")

    def rezygnuj(self):
        self.koniec(wygrana=True)

    def koniec(self, wygrana):
        if not wygrana and self.nr > PROG_GWARANTOWANY:
            self.nagroda = NAGRODY[PROG_GWARANTOWANY]

        wynik = {
            "data": datetime.now().isoformat(),
            "odpowiedzi": self.wyniki,
            "nagroda_koncowa": self.nagroda
        }

        wynik_path = RESULTS_DIR / f"wynik_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(wynik_path, "w", encoding="utf-8") as f:
            json.dump(wynik, f, indent=2, ensure_ascii=False)

        msg = f"🎉 Wygrałeś {self.nagroda} zł!" if wygrana else f"Gra zakończona. Twoja wygrana: {self.nagroda} zł"
        messagebox.showinfo("Wynik", msg)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")
    app = MilionerzyGra(root)
    root.mainloop()

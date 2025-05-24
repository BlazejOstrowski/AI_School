import tkinter as tk
from tkinter import messagebox
import os, json, random
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageTk
import openai
from dotenv import load_dotenv

# przygotowanie ścieżek
BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# OpenAI
load_dotenv()
openai.api_type = "azure"
openai.api_base = "https://openai-bost593.openai.azure.com"
openai.api_version = "2024-12-01-preview"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")
DEPLOYMENT_NAME = "gpt-4o"

# stałe gry
NAGRODY = [500, 1000, 2000, 5000]
PROG_GWARANTOWANY = 1  # po 2 poprawnych
TLO = BASE_DIR / "milionerzy_bg.jpg"


def pobierz_pytania():
    prompt = (
        "Stwórz 4 pytania quizowe w stylu Milionerzy. "
        "Każde pytanie ma 4 odpowiedzi A-D i poprawną jako 'answer'. "
        "Zwróć listę JSON: [{'question': '...', 'options': [...], 'answer': 'A'}]"
    )
    try:
        response = openai.ChatCompletion.create(
            engine=DEPLOYMENT_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response["choices"][0]["message"]["content"]
        import re
        czysty = re.sub(r"^```json|```$", "", text, flags=re.MULTILINE).strip()
        return json.loads(czysty)
    except Exception as e:
        print("Błąd pobierania pytań:", e)
        return []


class MilionerzyGra:
    def __init__(self, root):
        self.root = root
        self.root.title("Milionerzy")
        self.root.geometry("800x600")
        self.pytania = pobierz_pytania()
        self.nr = 0
        self.nagroda = 0
        self.odpowiedzi = []
        self.uzyto_5050 = False

        # tło
        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack(fill="both", expand=True)
        if TLO.exists():
            obraz = Image.open(TLO).resize((800, 600))
            self.bg = ImageTk.PhotoImage(obraz)
            self.canvas.create_image(0, 0, image=self.bg, anchor="nw")

        # GUI
        self.lbl_punkty = tk.Label(root, text="Punkty: 0 zł", font=("Arial", 12, "bold"), bg="white")
        self.lbl_punkty.place(x=50, y=10)

        self.lbl_pytanie = tk.Label(root, text="", wraplength=700, font=("Arial", 14), bg="white")
        self.lbl_pytanie.place(x=50, y=40)

        self.przyciski = []
        for i in range(4):
            btn = tk.Button(root, text="", font=("Arial", 12), width=50,
                            command=lambda i=i: self.odpowiedz(i))
            btn.place(x=150, y=120 + i * 60)
            self.przyciski.append(btn)

        self.btn_5050 = tk.Button(root, text="50:50", command=self.uzyj_5050)
        self.btn_5050.place(x=700, y=10)

        self.btn_rezygnuj = tk.Button(root, text="Zrezygnuj", command=self.rezygnuj)
        self.btn_rezygnuj.place(x=600, y=10)

        self.pokaz_pytanie()

    def pokaz_pytanie(self):
        if self.nr >= len(self.pytania):
            self.koniec(True)
            return

        p = self.pytania[self.nr]
        self.lbl_pytanie.config(text=f"{self.nr+1}. {p['question']}")
        for i in range(4):
            self.przyciski[i].config(text=p['options'][i], state="normal")
        self.lbl_punkty.config(text=f"Punkty: {self.nagroda} zł")

        if self.uzyto_5050:
            self.btn_5050.config(state="disabled")

    def odpowiedz(self, idx):
        pyt = self.pytania[self.nr]
        wybor = pyt["options"][idx][0]
        poprawna = pyt["answer"]

        poprawnie = wybor == poprawna
        self.odpowiedzi.append({
            "pytanie": pyt["question"],
            "odpowiedz": wybor,
            "poprawna": poprawna,
            "czy_poprawna": poprawnie,
            "nagroda": NAGRODY[self.nr]
        })

        if poprawnie:
            self.nagroda = NAGRODY[self.nr]
            self.nr += 1
            self.pokaz_pytanie()
        else:
            self.koniec(False)

    def uzyj_5050(self):
        if self.uzyto_5050:
            return
        pyt = self.pytania[self.nr]
        poprawna = pyt["answer"]
        do_usuniecia = [i for i in range(4) if pyt["options"][i][0] != poprawna]
        for i in random.sample(do_usuniecia, 2):
            self.przyciski[i].config(state="disabled")
        self.uzyto_5050 = True
        self.btn_5050.config(state="disabled")

    def rezygnuj(self):
        self.koniec(True)

    def koniec(self, wygrana):
        if not wygrana and self.nr > PROG_GWARANTOWANY:
            self.nagroda = NAGRODY[PROG_GWARANTOWANY]

        wynik = {
            "data": datetime.now().isoformat(),
            "odpowiedzi": self.odpowiedzi,
            "nagroda_koncowa": self.nagroda
        }

        path = RESULTS_DIR / f"wynik_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(wynik, f, indent=2, ensure_ascii=False)

        komunikat = f"Wygrałeś {self.nagroda} zł!" if wygrana else f"Zła odpowiedź. Wygrywasz {self.nagroda} zł."
        messagebox.showinfo("Koniec gry", komunikat)
        self.root.destroy()


if __name__ == "__main__":
    okno = tk.Tk()
    gra = MilionerzyGra(okno)
    okno.mainloop()

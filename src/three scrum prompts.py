import os
import openai
from dotenv import load_dotenv

# Wczytaj klucz z pliku .env
load_dotenv()

# Konfiguracja Azure OpenAI
openai.api_type = "azure"
openai.api_base = "https://openai-bost593.openai.azure.com"
openai.api_version = "2024-12-01-preview"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")

DEPLOYMENT_NAME = "gpt-4o"

# Prompt z kontekstem filmu (musisz podać streszczenie ręcznie!)
prompt = """
Na podstawie filmu 'Scrum in 20 mins' przedstawiającego podstawy Scruma:
- Product Owner dba o uporządkowany backlog
- Scrum Master prowadzi codzienne stand-upy
- Zespół developerski korzysta z tablicy zadań (np. Kanban)

Wygeneruj 3 user stories zgodne z zasadą INVEST. Każda powinna zawierać:
- opis roli, celu i wartości biznesowej
- 2–3 kryteria akceptacji
- format Markdown, gotowy do zapisania w pliku backlog/sprint1.md
"""

# Wysłanie prompta do GPT-4o
response = openai.ChatCompletion.create(
    engine=DEPLOYMENT_NAME,
    messages=[{"role": "user", "content": prompt}]
)

# Pobranie odpowiedzi
content = response["choices"][0]["message"]["content"]

# Upewnij się, że folder istnieje
os.makedirs("backlog", exist_ok=True)

# Zapisz do pliku markdown
with open("backlog/sprint1.md", "w", encoding="utf-8") as f:
    f.write(content)

print("Zobacz plik: backlog/sprint1.md")

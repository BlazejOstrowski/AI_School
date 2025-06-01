# AI School – GenAI Practice Projects

This is my personal project for learning how to work with GenAI tools, especially GPT models from Azure OpenAI.

## Goal

The main goal is to go through a GenAI Engineer learning path and build useful things using GPT, Python, and prompt engineering.

---

## What’s in the project

### 1. `main.py` – prompt usage logging

Sends a few prompts to GPT (like "history of Poland" or "quick potato meals"), logs the token usage, calculates cost, and writes everything to a `.md` file.

Used:
- `dotenv` to load the Azure API key
- `openai.ChatCompletion.create` for sending prompts
- `datetime`, `os`, basic file handling

---

### 2. `quiz_game.py` – console quiz game

A simple quiz game based on “Who Wants to Be a Millionaire?” (console version). It:

- shows questions
- checks answers
- gives increasing rewards
- ends on a wrong answer or when player stops

Run from terminal with:


python milionerzy.py play_game

# Milionerzy (Python Game)

This is a simple game inspired by the TV show "Who Wants to Be a Millionaire?"  
It’s written in Python using `tkinter` for the GUI and OpenAI (ChatGPT) to generate questions.

## What does the game do?

- gets 4 quiz questions from GPT
- displays them in a window
- keeps track of points and prize levels (like in the show)
- has a 50:50 lifeline (removes two wrong answers)
- lets the player quit and take the current prize
- saves the result to a `.json` file

### 3. `function_app.py` – Azure Function backend for RAG

This script defines two HTTP-triggered Azure Functions:

- `ask_rag` – receives a question, queries Azure Cognitive Search, and uses Azure OpenAI (GPT) to answer.
- `upload_pdf` – receives a PDF file, chunks it, embeds it using OpenAI Embeddings, and indexes it into Azure AI Search.

Also includes:
- automatic `traceId` logging per request
- endpoint `raise_error` for testing Application Insights monitoring

Used:
- Azure Functions Python v2 model with decorators
- `PyMuPDF` to extract text from PDF
- `langchain` retrievers and embeddings (partially replaced by native indexing)

---

### 4. `app.py` – Streamlit frontend

Provides a simple UI where the user can:

- enter questions (GETs `/api/ask_rag`)
- upload PDFs (POSTs `/api/upload_pdf`)
- trigger an intentional error for testing logs (`/api/raise_error`)

The answers and trace IDs are shown on screen.

---

### 5. Monitoring – Application Insights

- All logs and exceptions are visible in Azure's Application Insights.
- Each function call logs a unique `traceId` for tracking.
- `raise_error` helps verify if exceptions are correctly logged and queryable.

Use queries like:

kusto
exceptions | order by timestamp desc
traces | where message has "upload_pdf"

## How to run it

1. Install the required libraries:

```bash
pip install openai python-dotenv pillow


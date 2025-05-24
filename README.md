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

## How to run it

1. Install the required libraries:

```bash
pip install openai python-dotenv pillow


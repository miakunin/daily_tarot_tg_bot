# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Telegram bot for daily Tarot fortune readings with AI interpretations powered by Google Gemini. Written in Russian (UI strings, comments, docs). The bot enforces a one-reading-per-day limit per user.

## Running the Bot

```bash
python -m venv tarot_bot_env && source tarot_bot_env/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in BOT_TOKEN, optionally GEMINI_API_KEY and ADMIN_ID
python main.py
```

## Architecture

There are two versions of the bot in this repo:

1. **`bot.py`** (root) — the original monolithic version. Single-file implementation importing from a root-level `tarot_cards.py`.
2. **`main.py` + `bot/`** — the refactored modular version (current entry point).

The modular version follows this dependency flow:

```
main.py → Config → TarotBot
                      ├── AIService (Google Gemini)
                      ├── UserService → Database (JSON file storage)
                      ├── FortuneService (uses AIService + UserService)
                      └── Handlers (basic, fortune, stats, ai, admin, messages)
```

- **Config** (`bot/config.py`): loads env vars via `python-dotenv`. Required: `BOT_TOKEN`. Optional: `GEMINI_API_KEY`, `ADMIN_ID`.
- **Services** (`bot/services/`): business logic layer. `FortuneService` orchestrates card drawing, AI interpretation (with classic fallback), and user state updates.
- **Handlers** (`bot/handlers/`): Telegram command handlers. Each handler class receives services via constructor injection. Registered in `TarotBot._setup_handlers()`.
- **Models** (`bot/models/`): `TarotCard` and `User` dataclasses.
- **Data** (`bot/data/tarot_cards.py`): static deck of 78 cards (22 Major + 56 Minor Arcana) and fortune message templates.
- **Database**: JSON file at `bot/data/users/users_data.json` (gitignored). No external DB server needed.

## Key Libraries

- `python-telegram-bot` v22.1 — async Telegram Bot API wrapper
- `google-generativeai` — Google Gemini for AI card interpretations
- `python-dotenv` — env config

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `BOT_TOKEN` | Yes | Telegram bot token from @BotFather |
| `GEMINI_API_KEY` | No | Google Gemini API key for AI readings |
| `ADMIN_ID` | No | Telegram user ID for admin commands (`/reset`, `/adminstats`) |

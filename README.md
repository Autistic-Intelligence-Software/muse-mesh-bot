# MuseMeshBot

Telegram bot for multi-agent mesh synchronization, running on Railway.

## Setup

Set the `TELEGRAM_BOT_TOKEN` env var (from @BotFather) on the Railway service.

## Commands

- `/start` — check the bot is alive
- `/mesh_status` — show the current mesh task checklist

It also handles `EXECUTE_BROWSER:` JSON payloads (runs headless Chromium and
returns the page title) and logs `TO:` / `BROADCAST:` mesh traffic.

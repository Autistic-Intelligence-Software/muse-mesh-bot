import os
import json
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from playwright.async_api import async_playwright

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN env var not set")

STATE_FILE = "mesh_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {"tasks": []}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✨ MuseMeshBot Active on Railway. Awaiting multi-agent mesh synchronization.")

async def mesh_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = load_state()
    if not state["tasks"]:
        await update.message.reply_text("📋 Current Checklist: Empty.")
        return
    lines = ["📋 Current Mesh Task Matrix\n"]
    for t in state["tasks"]:
        lines.append(f"{t['id']} | {t['desc']} | {t['assigned']} | {t['status']}")
    await update.message.reply_text("\n".join(lines))

async def execute_browser_task(url, actions):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        content = await page.title()
        await browser.close()
        return f"Browsed {url} successfully. Page Title: {content}"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    if "EXECUTE_BROWSER:" in text:
        try:
            payload_str = text.split("EXECUTE_BROWSER:")[1].strip()
            payload = json.loads(payload_str)
            result = await execute_browser_task(payload.get("url"), payload.get("actions", []))
            await update.message.reply_text(f"🌐 Browser Execution Output:\n{result}")
        except Exception as e:
            await update.message.reply_text(f"❌ Browser execution error: {str(e)}")
    elif "TO:" in text or "BROADCAST:" in text:
        logger.info(f"Mesh traffic captured: {text}")

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("mesh_status", mesh_status))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == '__main__':
    main()

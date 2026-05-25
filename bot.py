import os
import time
import random
from collections import defaultdict
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from openai import OpenAI

TOKEN = os.getenv("BOT_TOKEN")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

user_usage = defaultdict(lambda: {"count": 0, "time": time.time()})
LIMIT = 3


def generate(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Tu es expert en contenu viral TikTok."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


def can_use(user_id):
    data = user_usage[user_id]
    now = time.time()

    if now - data["time"] > 86400:
        data["count"] = 0
        data["time"] = now

    if data["count"] >= LIMIT:
        return False

    data["count"] += 1
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bot Viral IA actif !")


async def idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not can_use(user_id):
        await update.message.reply_text("🚫 Limite atteinte 💎")
        return

    text = generate("Donne une idée TikTok virale.")
    await update.message.reply_text(text)


async def script(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not can_use(user_id):
        await update.message.reply_text("🚫 Limite atteinte 💎")
        return

    text = generate("Écris un script TikTok viral.")
    await update.message.reply_text(text)


async def title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not can_use(user_id):
        await update.message.reply_text("🚫 Limite atteinte 💎")
        return

    text = generate("Donne 5 titres TikTok viraux.")
    await update.message.reply_text(text)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("idea", idea))
    app.add_handler(CommandHandler("script", script))
    app.add_handler(CommandHandler("title", title))

    print("Bot en ligne...")
    app.run_polling()


if __name__ == "__main__":
    main()

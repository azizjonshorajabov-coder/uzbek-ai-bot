
import os
import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from google import genai

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AI_KEY = os.getenv("GEMINI_API_KEY")

if not TOKEN or not AI_KEY:
    raise RuntimeError("Bot tokeni yoki AI kaliti sozlanmagan!")

ai = genai.Client(api_key=AI_KEY)
history = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! 🇺🇿\n"
        "Men aqlli AI yordamchiman.\n"
        "Savolingizni yozing, sizga javob beraman!"
    )

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    question = update.message.text

    await update.message.chat.send_action("typing")

    old = history.get(user_id, [])
    prompt = (
        "Sen o'zbek tilida javob beradigan aqlli yordamchisan. "
        "Har doim o'zbek tilida, odobli va tushunarli javob ber. "
        "Agar bilmasang, bilmasligingni ayt.\n\n"
        + "\n".join(old)
        + f"\nFoydalanuvchi: {question}\nYordamchi:"
    )

    try:
        response = await asyncio.to_thread(
            ai.models.generate_content,
            model="gemini-2.5-flash",
            contents=prompt
        )

        result = response.text or "Kechirasiz, javob tayyorlay olmadim."

        history[user_id] = (
            old + [
                f"Foydalanuvchi: {question}",
                f"Yordamchi: {result}"
            ]
        )[-12:]

        await update.message.reply_text(result[:4000])

    except Exception:
        logging.exception("AI javobida xatolik")
        await update.message.reply_text(
            "Hozir javob berishda xatolik yuz berdi. "
            "Birozdan keyin qayta urinib ko'ring."
        )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))
    print("Uzbek AI bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()


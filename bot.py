import os
import requests
import pandas as pd

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
TWELVE_API_KEY = os.getenv("TWELVE_API_KEY")

last_photos = {}


def get_market_data(symbol):

    url = "https://api.twelvedata.com/time_series"

    params = {
        "symbol": symbol,
        "interval": "5min",
        "outputsize": 100,
        "apikey": TWELVE_API_KEY
    }

    r = requests.get(url, params=params, timeout=30)
    data = r.json()

    if "values" not in data:
        raise Exception(data)

    df = pd.DataFrame(data["values"])

    df["close"] = df["close"].astype(float)

    df = df.sort_values("datetime")

    return df


def calculate_rsi(df, period=14):

    delta = df["close"].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return round(float(rsi.iloc[-1]), 2)


def analyze_symbol(symbol):

    df = get_market_data(symbol)

    current_price = float(df["close"].iloc[-1])

    ma20 = float(df["close"].rolling(20).mean().iloc[-1])
    ma50 = float(df["close"].rolling(50).mean().iloc[-1])

    rsi = calculate_rsi(df)

    if ma20 > ma50:
        trend = "HAUSSIERE 📈"
    else:
        trend = "BAISSIERE 📉"

    if rsi < 30:
        state = "SURVENTE"
    elif rsi > 70:
        state = "SURACHAT"
    else:
        state = "NEUTRE"

    return {
        "price": current_price,
        "trend": trend,
        "rsi": rsi,
        "state": state
    }


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 ForexCryptoAIBot\n\n"
        "Envoie une capture ou utilise :\n\n"
        "/signal BTC/USD\n"
        "/signal ETH/USD\n"
        "/signal EUR/USD\n"
        "/signal GBP/USD\n"
        "/signal XAU/USD"
    )


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    photo = update.message.photo[-1]

    file = await photo.get_file()

    user_id = update.effective_user.id

    filename = f"{user_id}_chart.jpg"

    await file.download_to_drive(filename)

    last_photos[user_id] = filename

    await update.message.reply_text(
        "📸 Capture reçue.\n\n"
        "Maintenant utilise par exemple :\n"
        "/signal BTC/USD"
    )


async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not context.args:

        await update.message.reply_text(
            "Exemple : /signal BTC/USD"
        )
        return

    symbol = context.args[0].upper()

    try:

        result = analyze_symbol(symbol)

        message = (
            f"📊 {symbol}\n\n"
            f"Prix : {result['price']}\n"
            f"Tendance : {result['trend']}\n"
            f"RSI : {result['rsi']}\n"
            f"Etat : {result['state']}\n\n"
            f"⚠️ Analyse technique uniquement."
        )

        await update.message.reply_text(message)

    except Exception as e:

        await update.message.reply_text(
            f"Erreur : {e}"
        )


def main():

    if not BOT_TOKEN:
        raise Exception("BOT_TOKEN manquant")

    if not TWELVE_API_KEY:
        raise Exception("TWELVE_API_KEY manquant")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signal", signal))

    app.add_handler(
        MessageHandler(filters.PHOTO, photo_handler)
    )

    print("ForexCryptoAIBot lancé")

    app.run_polling()


if __name__ == "__main__":
    main()

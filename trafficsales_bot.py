import os
import telebot
from telebot import types
import smtplib
from email.mime.text import MIMEText
from flask import Flask, request, abort

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID"))
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

wallets = {
    "USDT (TRC20)": "TNSTLD5QoEWTfBUYCQS4tz1d6YCoNbFwzX",
    "ETH": "0x1ccec8467306195d2ceb0956e0d92dbd92d5115e",
    "SOL": "9cEaE1fbkEtSoezz7xMFjtdfS8N1QXE4g6TDsGmi9nFG"
}

user_data = {}

def send_email(subject, message):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Email sending failed: {e}")

def forward_to_admin(chat_id, text):
    bot.send_message(ADMIN_TELEGRAM_ID, f"Message from {chat_id}:\n{text}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    forward_to_admin(message.chat.id, "/start command invoked")
    welcome_text = (
        "🚀 Welcome to *Ad Traffic Bot*\n"
        "Real Traffic That Brings Results!\n\n"
        "We deliver *premium-quality traffic* using:\n"
        "✅ Google Ads\n"
        "✅ Meta (Facebook) Ads\n"
        "✅ Push & Native Advertising\n\n"
        "📌 No bots. No fake clicks. No garbage traffic.\n"
        "💥 Real people – bringing *real sales and leads*.\n\n"
        "🧠 Perfect for:\n"
        "• E-Commerce websites (Dropshipping, Shopify)\n"
        "• Affiliate & CPA campaigns\n"
        "• Service websites (SMMA, freelancers, SaaS)\n"
        "• Grayhat / Blackhat niches\n"
        "• Crypto, NFT, casino & betting landing pages\n"
        "• Lead generation forms\n"
        "• SEO tests, heatmaps, behavioral analysis\n\n"
        "💵 Minimum order: $100\n"
        "🌍 Geo-targeted: US/CA, Asia, EU or Worldwide\n"
        "💳 We accept: *USDT (TRC20), ETH, SOL*\n"
        "📩 Detailed report sent by email after delivery\n\n"
        "🔥 Ready to scale with real traffic? Let’s go!\n"
        "Type /start or tap below to begin your order."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")
    user_data[message.chat.id] = {}
    bot.register_next_step_handler(message, get_project_desc)

def get_project_desc(message):
    forward_to_admin(message.chat.id, message.text)
    user_data[message.chat.id]['project'] = message.text
    bot.send_message(message.chat.id, "Great! Now send me your website URL:")
    bot.register_next_step_handler(message, get_url)

def get_url(message):
    forward_to_admin(message.chat.id, message.text)
    user_data[message.chat.id]['url'] = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("US/CA", "Europe", "Asia", "Worldwide")
    bot.send_message(message.chat.id, "Choose your target GEO:", reply_markup=markup)
    bot.register_next_step_handler(message, get_geo)

def get_geo(message):
    forward_to_admin(message.chat.id, message.text)
    geo = message.text
    user_data[message.chat.id]['geo'] = geo

    prices = {
        "US/CA": [(2000, 100), (5500, 250), (12000, 500), (25000, 999)],
        "Europe": [(2500, 100), (6500, 250), (14000, 500), (28000, 999)],
        "Asia": [(5000, 100), (13000, 250), (28000, 500), (50000, 999)],
        "Worldwide": [(3500, 100), (9000, 250), (19000, 500), (35000, 999)]
    }

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for visits, price in prices.get(geo, []):
        markup.add(f"{visits} visits - ${price}")

    bot.send_message(message.chat.id, "Choose your package:", reply_markup=markup)
    bot.register_next_step_handler(message, get_package)

def get_package(message):
    forward_to_admin(message.chat.id, message.text)
    user_data[message.chat.id]['package'] = message.text
    bot.send_message(message.chat.id, "Specific country? If yes, type it. Otherwise, type 'No':")
    bot.register_next_step_handler(message, get_specific_country)

def get_specific_country(message):
    forward_to_admin(message.chat.id, message.text)
    user_data[message.chat.id]['country'] = message.text
    bot.send_message(message.chat.id, "Enter your email address for reports:")
    bot.register_next_step_handler(message, get_email)

def get_email(message):
    forward_to_admin(message.chat.id, message.text)
    user_data[message.chat.id]['email'] = message.text
    wallet_text = "\n".join([f"{k}: `{v}`" for k, v in wallets.items()])
    bot.send_message(message.chat.id, f"Send payment to:\n\n{wallet_text}\n\nYou'll receive your traffic report via email. ✅", parse_mode="Markdown")

    summary = '\n'.join([f"{k.capitalize()}: {v}" for k, v in user_data[message.chat.id].items()])
    bot.send_message(ADMIN_TELEGRAM_ID, f"New Traffic Order:\n\n{summary}")
    send_email("New Traffic Order", summary)
    bot.send_message(message.chat.id, "Thank you! Your order is recorded. We'll notify you after payment confirmation.")

@app.route('/', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return '', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

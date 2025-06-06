import telebot
from telebot import types
import smtplib
from email.mime.text import MIMEText
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID"))
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

bot = telebot.TeleBot(BOT_TOKEN)

wallets = {
    "USDT (TRC20)": "TNSTLD5QoEWTfBUYCQS4tz1d6YCoNbFwzX",
    "USDT (ERC20)": "0x1ccec8467306195d2ceb0956e0d92dbd92d5115e",
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
    bot.send_message(message.chat.id, (
        "👋 Welcome to *Real Ad Traffic* Bot!\n\n"
        "We deliver 100% real human traffic using:\n"
        "✅ Google Ads\n"
        "✅ Meta (Facebook/Instagram) Ads\n"
        "✅ Push & Native Ad Networks\n\n"
        "🚫 No fake/bot traffic. No free junk. Just real leads, sales & growth.\n\n"
        "Perfect for:\n"
        "- E-commerce websites (dropshipping, affiliate included)\n"
        "- Service websites\n"
        "- Lead generation pages\n"
        "- Any project that needs real users!\n\n"
        "💬 For questions or issues, DM @DestinationUnknowns\n\n"
        "👉 Let's get started! Tell me your website niche or what your project is about:"
    ), parse_mode="Markdown")
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

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    options = prices.get(geo, [])
    for visits, price in options:
        markup.add(f"{visits} visits - ${price}")

    bot.send_message(message.chat.id, "Choose a package:", reply_markup=markup)
    bot.register_next_step_handler(message, get_package)

def get_package(message):
    forward_to_admin(message.chat.id, message.text)
    user_data[message.chat.id]['package'] = message.text
    bot.send_message(message.chat.id, "(Optional) Do you want traffic from a specific country? If yes, type the country. If not, type 'No':")
    bot.register_next_step_handler(message, get_specific_country)

def get_specific_country(message):
    forward_to_admin(message.chat.id, message.text)
    user_data[message.chat.id]['country'] = message.text
    bot.send_message(message.chat.id, "Now enter your email address for reports:")
    bot.register_next_step_handler(message, get_email)

def get_email(message):
    forward_to_admin(message.chat.id, message.text)
    user_data[message.chat.id]['email'] = message.text
    wallet_text = "\n".join([f"{k}: `{v}`" for k, v in wallets.items()])
    bot.send_message(message.chat.id, f"Send payment to:\n\n{wallet_text}\n\nYou'll receive the report via email. ✅", parse_mode="Markdown")

    summary = '\n'.join([f"{k.capitalize()}: {v}" for k, v in user_data[message.chat.id].items()])
    bot.send_message(ADMIN_TELEGRAM_ID, f"New Traffic Order:\n\n{summary}")
    send_email("New Traffic Order", summary)
    bot.send_message(message.chat.id, "Thank you! Your order is recorded. We will notify you after payment confirmation.")

bot.infinity_polling()

import telebot
from telebot import types
import smtplib
from email.mime.text import MIMEText

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ADMIN_TELEGRAM_ID = 123456789  # Replace with your Telegram ID
EMAIL_RECEIVER = "mumodanet@gmail.com"
EMAIL_SENDER = "your_email@gmail.com"
EMAIL_PASSWORD = "your_email_password"
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
    bot.send_message(message.chat.id, f"""
👋 Welcome to *Real Ad Traffic* Bot!

We deliver 100% real human traffic using:
✅ Google Ads
✅ Meta (Facebook/Instagram) Ads
✅ Push & Native Ad Networks

🚫 No fake/bot traffic. No free junk. Just real leads, sales & growth.

Perfect for:
- E-commerce websites (dropshipping, affiliate included)
- Service websites
- Lead generation pages
- Any project that needs real users!

💬 For questions or issues, DM @DestinationUnknowns

👉 Let's get started! Tell me your website niche or what your project is about:
""", parse_mode="Markdown")
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

    text = "Choose a package:\n"
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for visits, price in prices.get(geo, []):
        option = f"{visits} visits - ${price}"
        markup.add(option)
        text += option + "\n"

    bot.send_message(message.chat.id, text, reply_markup=markup)
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
    text = "Please send your payment to one of the following wallets:\n\n"
    for name, address in wallets.items():
        text += f"{name}: `{address}`\n"
    text += "\nOnce payment is made, you will receive your traffic report via email. ✅"
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

    data = user_data[message.chat.id]
    summary = f"New Traffic Order Received:\n\n"
    summary += f"Project: {data['project']}\nURL: {data['url']}\nGEO: {data['geo']}\nPackage: {data['package']}\nSpecific Country: {data['country']}\nEmail: {data['email']}\n"

    bot.send_message(ADMIN_TELEGRAM_ID, summary)
    send_email("New Traffic Order", summary)
    bot.send_message(message.chat.id, "Thank you! Your order is recorded. We will notify you after payment confirmation.")

bot.infinity_polling()

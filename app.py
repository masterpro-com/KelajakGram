import telebot

TOKEN = "8528236172:AAFQ3st4r32JgtRf8ZhQGDZe69aAcwngruw"

bot = telebot.TeleBot(TOKEN)

# /start buyrug‘i
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id,
        "Salom 👋\nBu mening birinchi Telegram botim 🤖"
    )

# Oddiy xabarlarni qaytarish (echo)
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.send_message(message.chat.id, f"Siz yozdingiz: {message.text}")

print("Bot ishga tushdi...")
bot.polling()
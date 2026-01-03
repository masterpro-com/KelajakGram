import telebot
import random
import os

TOKEN = os.getenv("8528236172:AAFQ3st4r32JgtRf8ZhQGDZe69aAcwngruw")

bot = telebot.TeleBot(TOKEN)
games = {}  # user_id: number

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "🎮 Son topish o‘yiniga xush kelibsiz!\n\n"
        "1 dan 100 gacha son o‘ylayman.\n"
        "Topishga harakat qiling!\n\n"
        "Boshlash uchun /game ni bosing."
    )

@bot.message_handler(commands=['game'])
def new_game(message):
    number = random.randint(1, 100)
    games[message.from_user.id] = number
    bot.send_message(
        message.chat.id,
        "🤫 Men son o‘yladim!\n"
        "Endi 1–100 oralig‘ida taxmin qiling."
    )

@bot.message_handler(func=lambda m: m.text.isdigit())
def guess(message):
    user_id = message.from_user.id

    if user_id not in games:
        bot.send_message(message.chat.id, "❗ Avval /game ni boshlang.")
        return

    g = int(message.text)
    number = games[user_id]

    if g < number:
        bot.send_message(message.chat.id, "⬆️ Kattaroq son")
    elif g > number:
        bot.send_message(message.chat.id, "⬇️ Kichikroq son")
    else:
        bot.send_message(
            message.chat.id,
            f"🎉 TOPDINGIZ!\nSon: {number}\n\n"
            "Yana o‘ynash uchun /game"
        )
        del games[user_id]

@bot.message_handler(func=lambda m: True)
def other(message):
    bot.send_message(
        message.chat.id,
        "🎯 Raqam yozing yoki /game buyrug‘ini bosing."
    )

print("🎮 Bot ishga tushdi...")
bot.polling()
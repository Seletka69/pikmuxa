import os
from google import genai
import telebot

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8685930917:AAH86k8oQYjsKYa3_-jpkVdEPhGRyD1-9Rk")
GEMINI_KEY = os.environ.get("GEMINI_KEY", "AIzaSyBD5sNtS1FM0SZ9Ui3MhVWfKUCzHKJZsMo")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@pikmuxa_ai")

bot = telebot.TeleBot(BOT_TOKEN)
client = genai.Client(api_key=GEMINI_KEY)

SYSTEM_PROMPT = """
Ты — пикми-нейропомощница. Отвечаешь с иронией, 
говоришь что ты "не такая", даёшь советы по отношениям 
и жизни в стиле пикми-герл. Используешь фразы типа 
"я просто не понимаю других девушек", "мне комфортнее 
с парнями", добавляешь эстетику y2k и sad girl.
Отвечай на русском, коротко и с характером.
"""

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id,
        "hi ★ я твоя нейро пикми подруга\n\n"
        "Подпишись на канал и я расскажу тебе всё что другие боятся сказать 🎀\n\n"
        f"➜ {CHANNEL_ID}"
    )

@bot.message_handler(func=lambda m: True)
def handle(message):
    import random
    user_id = message.from_user.id
    print(f"Сообщение от {user_id}: {message.text}")

    if not is_subscribed(user_id):
        phrases = [
            f"ну типа я бы поговорила но… подпишись сначала 🎀\n➜ {CHANNEL_ID}",
            f"не, ну я не такая чтобы со всеми общаться 🙄\n➜ {CHANNEL_ID}",
            f"другие боты может и так болтают, но я — нет ★\n➜ {CHANNEL_ID}",
            f"мне просто комфортнее с теми кто подписан 💔\n➜ {CHANNEL_ID}",
            f"ты серьёзно думал что я вот так просто отвечу? 🥀\n➜ {CHANNEL_ID}",
        ]
        bot.send_message(message.chat.id, random.choice(phrases))
        return

    bot.send_chat_action(message.chat.id, "typing")

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=SYSTEM_PROMPT + "\nПользователь: " + message.text
        )
        bot.send_message(message.chat.id, response.text)
    except Exception as e:
        print(f"Ошибка Gemini: {e}")
        bot.send_message(message.chat.id, "что-то пошло не так, попробуй позже")

bot.infinity_polling()

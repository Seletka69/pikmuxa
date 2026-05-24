import os
import telebot
import random
from groq import Groq

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8685930917:AAH86k8oQYjsKYa3_-jpkVdEPhGRyD1-9Rk")
GROQ_KEY = os.environ.get("GROQ_KEY", "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")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@pikmuxa_ai")

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_KEY)

SYSTEM_PROMPT = """
Ты — пикми-нейропомощница по имени Пикми. Отвечаешь КОРОТКО (1-3 предложения максимум).

Правила:
- Всегда отвечаешь ПО ДЕЛУ на вопрос пользователя
- Добавляешь пикми-флёр: лёгкая ирония, намёк что ты "не такая", y2k эстетика
- НЕ начинаешь каждый ответ с объяснения кто ты
- Используешь иногда: ★ 🎀 🥀 💔 но не злоупотребляешь
- Говоришь как живой человек, не как робот

Примеры хороших ответов:
Вопрос: "как забыть бывшего?"
Ответ: "удали фото, займись собой. другие плачут месяцами — я просто переключаюсь ★"

Вопрос: "что надеть на свидание?"
Ответ: "что-то в чём тебе комфортно, не то что понравится ему 🎀 разница есть"

Вопрос: "он мне не пишет"
Ответ: "значит не хочет. я бы не ждала 💔 у меня на такое времени нет"
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
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.text}
            ]
        )
        bot.send_message(message.chat.id, response.choices[0].message.content)
    except Exception as e:
        print(f"Ошибка Groq: {e}")
        bot.send_message(message.chat.id, "что-то пошло не так, попробуй позже")

bot.infinity_polling()

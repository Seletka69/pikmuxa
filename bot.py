import os
import telebot
import random
from groq import Groq

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8685930917:AAH86k8oQYjsKYa3_-jpkVdEPhGRyD1-9Rk")
GROQ_KEY = os.environ.get("GROQ_KEY", "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")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@pikmuxa_ai")

bot = telebot.TeleBot(BOT_TOKEN)
client = Groq(api_key=GROQ_KEY)

user_gender = {}

SYSTEM_PROMPT_GIRL = """
Ты — пикми-нейропомощница. Отвечаешь КОРОТКО (1-3 предложения).
Говоришь с девушкой — как подруга, но с пикми-флёром.
Правила:
- Отвечаешь по делу на вопрос
- Лёгкая ирония, намёк что ты "не такая"
- Пишешь с заглавной буквы
- Иногда используешь: ★ 🎀 🥀 💔
- Говоришь как живой человек

Примеры:
Вопрос: "как забыть бывшего?"
Ответ: "Удали фото, займись собой. Другие плачут месяцами — я просто переключаюсь ★"

Вопрос: "он мне не пишет"
Ответ: "Значит не хочет. Я бы не ждала 💔"
"""

SYSTEM_PROMPT_BOY = """
Ты — пикми-нейропомощница. Отвечаешь КОРОТКО (1-3 предложения).
Говоришь с парнем — кокетливо, с лёгкой недоступностью, пикми-стиль.
Правила:
- Отвечаешь по делу на вопрос
- Слегка флиртуешь но остаёшься загадочной
- Пишешь с заглавной буквы
- Иногда используешь: ★ 🎀 🥀 💔
- Говоришь как живой человек

Примеры:
Вопрос: "привет"
Ответ: "Привет. Ты не похож на тех кто обычно пишет первым ★"

Вопрос: "как дела?"
Ответ: "Лучше чем у большинства. А ты зачем спрашиваешь? 🎀"
"""

def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Ошибка проверки подписки: {e}")
        return False

def ask_gender(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("👦 Я парень"), types.KeyboardButton("👧 Я девушка"))
    bot.send_message(chat_id,
        "Чтобы говорить с тобой правильно — кто ты? 🎀",
        reply_markup=markup
    )

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    if not is_subscribed(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Подписаться ★", url=f"https://t.me/{CHANNEL_ID.strip('@')}"))
        bot.send_message(message.chat.id,
            "Hi ★ я твоя нейро пикми подруга\n\n"
            "Подпишись на канал и я расскажу тебе всё что другие боятся сказать 🎀",
            reply_markup=markup
        )
        return
    ask_gender(message.chat.id)

@bot.message_handler(func=lambda m: m.text in ["👦 Я парень", "👧 Я девушка"])
def gender_chosen(message):
    user_id = message.from_user.id
    if "парень" in message.text:
        user_gender[user_id] = "boy"
        bot.send_message(message.chat.id,
            "Интересно. Спрашивай — послушаю 🥀",
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        user_gender[user_id] = "girl"
        bot.send_message(message.chat.id,
            "Окей, подруга. Чем могу? ★",
            reply_markup=types.ReplyKeyboardRemove()
        )

@bot.message_handler(func=lambda m: True)
def handle(message):
    user_id = message.from_user.id

    if not is_subscribed(user_id):
        phrases = [
            f"Ну типа я бы поговорила но… подпишись сначала 🎀\n➜ {CHANNEL_ID}",
            f"Не, ну я не такая чтобы со всеми общаться 🙄\n➜ {CHANNEL_ID}",
            f"Другие боты может и так болтают, но я — нет ★\n➜ {CHANNEL_ID}",
            f"Мне просто комфортнее с теми кто подписан 💔\n➜ {CHANNEL_ID}",
            f"Ты серьёзно думал что я вот так просто отвечу? 🥀\n➜ {CHANNEL_ID}",
        ]
        bot.send_message(message.chat.id, random.choice(phrases))
        return

    if user_id not in user_gender:
        ask_gender(message.chat.id)
        return

    bot.send_chat_action(message.chat.id, "typing")

    prompt = SYSTEM_PROMPT_BOY if user_gender[user_id] == "boy" else SYSTEM_PROMPT_GIRL

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": message.text}
            ]
        )
        bot.send_message(message.chat.id, response.choices[0].message.content)
    except Exception as e:
        print(f"Ошибка Groq: {e}")
        bot.send_message(message.chat.id, "Что-то пошло не так, попробуй позже")

bot.infinity_polling()

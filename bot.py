import os
import telebot
import google.generativeai as genai

BOT_TOKEN = "8685930917:AAH86k8oQYjsKYa3_-jpkVdEPhGRyD1-9Rk"
GEMINI_KEY = "AIzaSyBD5sNtS1FM0SZ9Ui3MhVWfKUCzHKJZsMo"
CHANNEL_ID = "@pikmuxa_ai"

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

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
    except:
        return False

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id,
        "𝒉𝒊 ★ я твоя нейро пикми подруга\n\n"
        "Подпишись на канал и я расскажу тебе всё что другие боятся сказать 🎀\n\n"
        f"➜ {CHANNEL_ID}"
    )

@bot.message_handler(func=lambda m: True)
def handle(message):
    user_id = message.from_user.id
    
    if not is_subscribed(user_id):
        bot.send_message(message.chat.id,
            "подпишись сначала 🙄\n"
            f"➜ {CHANNEL_ID}\n\n"
            "потом можем поговорить ★"
        )
        return
    
    bot.send_chat_action(message.chat.id, "typing")
    
    prompt = SYSTEM_PROMPT + "\nПользователь: " + message.text
    response = model.generate_content(prompt)
    
    bot.send_message(message.chat.id, response.text)

bot.polling()

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from logic import *
import schedule
import threading
import time
from config import *
import os
import cv2

bot = TeleBot(API_TOKEN)

def gen_markup(id):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton("Получить!", callback_data=id))
    return markup

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):

    prize_id = call.data
    user_id = call.message.chat.id

    if manager.get_winners_count(prize_id)<3:
        res = manager.add_winner(user_id, prize_id)
        if res:
            img = manager.get_prize_img(prize_id)
            with open(f'img/{img}', 'rb') as photo:
                bot.send_photo(user_id, photo, caption="Поздравляем! Ты получил картинку!")
        else:
            bot.send_message(user_id, 'Ты уже получил картинку!')
    else:
        bot.send_message(user_id, "К сожалению, ты не успел получить картинку! Попробуй в следующий раз!)")


def send_message():
    prize_id, img = manager.get_random_prize()[:2]
    manager.mark_prize_used(prize_id)
    hide_img(img)
    for user in manager.get_users():
        with open(f'hidden_img/{img}', 'rb') as photo:
            bot.send_photo(user, photo, reply_markup=gen_markup(id = prize_id))
        

def shedule_thread():
    schedule.every().minute.do(send_message) # Здесь ты можешь задать периодичность отправки картинок
    while True:
        schedule.run_pending()
        time.sleep(1)

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    if user_id in manager.get_users():
        bot.reply_to(message, "Ты уже зарегестрирован!")
    else:
        manager.add_user(user_id, message.from_user.username)
        bot.reply_to(message, """Привет! Добро пожаловать! 
Тебя успешно зарегистрировали!
Каждый час тебе будут приходить новые картинки и у тебя будет шанс их получить!
Для этого нужно быстрее всех нажать на кнопку 'Получить!'

Только три первых пользователя получат картинку!)""")

@bot.message_handler(commands=['rating'])
def handle_rating(message):
    res = manager.get_rating() 
    res = [f'| @{x[0]:<11} | {x[1]:<11}|\n{"_"*26}' for x in res]
    res = '\n'.join(res)
    res = f'|USER_NAME    |COUNT_PRIZE|\n{"_"*26}\n' + res
    bot.send_message(message.chat.id, res)
            
@bot.message_handler(commands=['get_my_score'])
def handle_get_my_score(message):
    user_id = message.chat.id

    info = manager.get_winners_img(user_id)
    if not info:
        bot.send_message(user_id, "У тебя пока нет полученных призов 😢")
        return

    prizes = [x[0] for x in info]

    all_images = os.listdir('img')
    image_paths = [
        f'img/{x}' if x in prizes else f'hidden_img/{x}'
        for x in all_images
    ]

    collage = create_collage(image_paths)

    if collage is None:
        bot.send_message(user_id, "Не удалось создать коллаж 😕")
        return

    collage_path = f'collage_{user_id}.jpg'
    cv2.imwrite(collage_path, collage)

    with open(collage_path, 'rb') as photo:
        bot.send_photo(user_id, photo, caption="🎉 Твои призы!")

    os.remove(collage_path)

def polling_thread():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    manager = DatabaseManager(DATABASE)
    manager.create_tables()

    polling_thread = threading.Thread(target=polling_thread)
    polling_shedule  = threading.Thread(target=shedule_thread)

    polling_thread.start()
    polling_shedule.start()
  

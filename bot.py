import logging
import telebot
import time
from telebot import types
from telegram_bot_pagination import InlineKeyboardPaginator

import operations
import messages_to_user
from config import DB_ADDRESS_OPERATIONS, TOKEN, BOT_INTERVAL, BOT_TIMEOUT

logging.basicConfig(filename='operations.log', format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)


def bot_polling():
    for _ in range(10):
        try:
            logging.info("New bot instance started")
            bot = telebot.TeleBot(TOKEN)
            bot_actions(bot)
            bot.polling(none_stop=True, interval=BOT_INTERVAL, timeout=BOT_TIMEOUT)
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt")
            bot.stop_polling()
            return
        except Exception as e:
            logging.error(f"Bot polling failed, restarting in {BOT_TIMEOUT} sec. Error: {e}")
            bot.stop_polling()
            sleep(BOT_TIMEOUT)
            
    bot.stop_polling()
    logging.error("Bot polling loop finished - out of tryings")


def bot_actions(bot):
    """
    All bot functions in a wrap
    """
      
    def add_item(message):
        url = message.text.strip()
        user = message.from_user.username
        
        result = operations.add_item_to_database(url, user)
        if result == 'Already_exist':
            bot.send_message(message.chat.id, 'Этот продукт уже находится в вашем списке наблюдения',
                            reply_markup=kboard)
        elif result == 'Added':
            bot.send_message(message.chat.id, 'Продукт добавлен в ваш список наблюдения',
                            reply_markup=kboard)
        else:
            bot.send_message(message.chat.id, 'Ошибка добавления - ссылка не может быть обработана',
                            reply_markup=kboard)
    
    
    def remove_item(message):
        ID = message.text.strip()
        user = message.from_user.username
        
        if ID.isdigit():            
            result = operations.remove_item_from_watch(ID, user)
            if result == "Not_in_list":
                bot.send_message(message.chat.id, f"ID {ID} не найден в вашем списке наблюдения",
                                reply_markup=kboard)
            elif result == "Removed":
                bot.send_message(message.chat.id, f"ID {ID} удален из списка наблюдения",
                                reply_markup=kboard)
            else:
                bot.send_message(message.chat.id, f"ID {ID} ворует-убивает гусей",
                                reply_markup=kboard)
        else:
            bot.send_message(message.chat.id, f"ID - это число. Кажется, вы пытаетесь записать что-то иное",
                            reply_markup=kboard)
    
            
    def get_items(message, isCallback=False, page=1):
        user = message.from_user.username
    #     user = 'root'
        result = operations.get_list_of_items_on_watch(user)
        if not result:
            answer = ["У вас нет продуктов в списке наблюдения"]
        else:    
            answer = []
            for i in range(0, len(result), 12):
                batch = result[i:i+12]
                answer.append("\n".join([f"id {i['id']}: {i['name']}" for i in batch]))
        
        paginator = InlineKeyboardPaginator(
            len(answer),
            current_page=page,
            data_pattern='items#{page}'
        )
        if isCallback:
            bot.edit_message_text(
                chat_id=message.chat.id,
                text=answer[page-1],
                message_id=message.message_id,
                reply_markup=paginator.markup,
                parse_mode='Markdown'
            )
        else:
            bot.send_message(
                message.chat.id,
                answer[page-1],
                reply_markup=paginator.markup,
                parse_mode='Markdown'
            )
    
            
    def get_profits(message, isCallback=False, page=1):
        user = message.from_user.username
    #     user = 'root'
        result = operations.get_list_of_profits_for_user(user, abs_profit_threshold=10)
        if not result:
            answer = ["Сегодня не ваш день - по скидонькам ничего нет :("]
        else:
            answer = []
            for i in range(0, len(result), 5):
                batch = result[i:i+5]
                formatted_message = "\n".join(
                    [f"*{i['name']}*\n\
     Сейчас: {i['price_last']}р, в среднем: {i['price_mean']}р\n\
     Профит: {i['abs_profit']}р ({i['relt_profit']})\n" for i in batch]
                )
                answer.append(formatted_message)
            
        paginator = InlineKeyboardPaginator(
            len(answer),
            current_page=page,
            data_pattern='profits#{page}'
        )
        if isCallback:
            bot.edit_message_text(
                chat_id=message.chat.id,
                text=answer[page-1],
                message_id=message.message_id,
                reply_markup=paginator.markup,
                parse_mode='Markdown'
            )
        else:
            bot.send_message(
                message.chat.id,
                answer[page-1],
                reply_markup=paginator.markup,
                parse_mode='Markdown'
            )
    
            
    def feedback(message):
        with open('feedback.txt', 'a') as file:
            file.write(f"Message from user {message.from_user.username}:\t")
            file.write(message.text)
            file.write('\n')
            bot.send_message(message.chat.id, "Cпасибо! Мы обратим на это внимание",
                            reply_markup=kboard)
    
            
    def add_demo(message):
        user = message.from_user.username
        if operations.add_demo_for_user(user):
            bot.send_message(message.chat.id, "Демо-база подключена", reply_markup=kboard)
        else:
            bot.send_message(message.chat.id, "Ошибка подключения базы", reply_markup=kboard)
    
            
            
    # set standard keyboard
    kboard=types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_add=types.KeyboardButton("Добавить продукт")
    button_show=types.KeyboardButton("Мой список")
    button_remove=types.KeyboardButton("Удалить продукт")
    button_get=types.KeyboardButton("А что по акции?")
    
    kboard.row(button_add, button_show, button_remove)
    kboard.row(button_get)
    
    # set blank keyboard
    kboard_blank=telebot.types.ReplyKeyboardRemove()
    
    
    
    @bot.message_handler(commands=['start'])
    def start_message(message):
        bot.send_message(message.chat.id, messages_to_user.welcome_message, reply_markup=kboard)
        
    @bot.message_handler(commands=['feedback'])
    def feedback_message(message):
        bot.send_message(message.chat.id,"Спасибо за фидбек! Опишите, пожалуйста, проблему (текстом)",
                        reply_markup=kboard_blank)
        bot.register_next_step_handler(message, feedback)
    
    @bot.message_handler(commands=['demo'])
    def demo_message(message):
        add_demo(message)
    
    @bot.message_handler(commands=['help'])
    def help_message(message):
        bot.send_message(message.chat.id, messages_to_user.help_message, reply_markup=kboard)
            
    @bot.message_handler(content_types='text')
    def message_reply(message):
        if message.text=="Добавить продукт":
            bot.send_message(message.chat.id, "Пришлите URL продукта, который хотите добавить",
                             reply_markup=kboard_blank)
            bot.register_next_step_handler(message, add_item)
            
        elif message.text=="Мой список":
            get_items(message)
    
        elif message.text=="Удалить продукт":
            bot.send_message(message.chat.id, "ID продукта, который вы хотите удалить?",
                             reply_markup=kboard_blank)
            bot.register_next_step_handler(message, remove_item)
            
        elif message.text=="А что по акции?":
            get_profits(message)
            
        else:
            bot.send_message(message.chat.id, "Команда не распознана. Доступные опции перечислены в /start",
                             reply_markup=kboard)
            
    @bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='items')
    def items_page_callback(call):
        page = int(call.data.split('#')[1])
        get_items(call.message, True, page)
        
    @bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='profits')
    def profits_page_callback(call):
        page = int(call.data.split('#')[1])
        get_profits(call.message, True, page)
    
    
bot_polling()

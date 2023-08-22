import telebot
import threading

import config
import text
import functions
import keyboards


bot = telebot.TeleBot(config.TELEGRAM_TOKEN, disable_notification=True)


@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id

    if not functions.is_in_database(user_id):
        user_username = message.from_user.username
        functions.add_user(user_id, user_username)

    bot.send_message(chat_id=message.chat.id,
                     text=text.START_MESSAGE,
                     parse_mode='Markdown',
                     )
    

@bot.message_handler(commands=['cancel'])
def start_message(message):
    message_id = functions.get_message_id(message.from_user.id)

    try:
        bot.delete_message(chat_id=message.chat.id,
                           message_id=message_id,
                           )
    except:
        pass

    functions.set_busy(message.from_user.id, False)

    bot.send_message(chat_id=message.chat.id,
                     text=text.CANCELED_REQUESTS,
                     )


@bot.message_handler(commands=['reload'])
def start_message(message):
    functions.update_history(message.from_user.id, '[]')

    bot.send_message(chat_id=message.chat.id,
                     text=text.CLEAR_HISTORY,
                     )


@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(chat_id=message.chat.id,
                     text=text.HELP_MESSAGE,
                     parse_mode='Markdown',
                     )


@bot.message_handler(commands=['good', 'bad'])
def start_message(message):
    user_id = str(message.from_user.id)
    if user_id in config.MANAGER_ID:
        if config.REPORT_FLAG:
            bot.send_message(chat_id=message.chat.id,
                         text=text.GENERATING_REPORT,
                         )
        else:
            config.REPORT_FLAG = True

            if 'good' in message.text:
                quality = 'good'
            elif 'bad' in message.text:
                quality = 'bad'

            threading.Thread(daemon=True, 
                        target=functions.handle_new_report_request, 
                        args=(user_id, quality,),
                        ).start()
    else:
        bot.send_message(chat_id=message.chat.id,
                         text=text.PROHIBITED,
                         )


@bot.message_handler(commands=['good_all', 'bad_all'])
def start_message(message):
    user_id = str(message.from_user.id)
    if user_id in config.MANAGER_ID:
        if config.REPORT_FLAG:
            bot.send_message(chat_id=message.chat.id,
                         text=text.GENERATING_REPORT,
                         )
        else:
            config.REPORT_FLAG = True

            if 'good' in message.text:
                quality = 'good'
            elif 'bad' in message.text:
                quality = 'bad'

            threading.Thread(daemon=True, 
                        target=functions.handle_all_report_request, 
                        args=(user_id, quality,),
                        ).start()
    else:
        bot.send_message(chat_id=message.chat.id,
                         text=text.PROHIBITED,
                         )


@bot.callback_query_handler(func = lambda call: True)
def callback_query(call):
    """Handles queries from inline keyboards."""

    # getting message's and user's ids
    message_id = call.message.id
    chat_id = call.message.chat.id

    call_data = call.data.split('_')
    query = call_data[0]

    if query == 'good' or query == 'bad':
        bot.edit_message_reply_markup(chat_id=chat_id,
                                      message_id=message_id,
                                      reply_markup=telebot.types.InlineKeyboardMarkup(),
                                      )
        
        question = call.message.reply_to_message.text
        answer = call.message.text 

        functions.add_answer(question, answer, query)



@bot.message_handler(content_types=['text'])
def handle_text(message):
    """Handles message with text type."""

    user_id = message.from_user.id
    chat_id = message.chat.id

    user_info = functions.get_info(user_id)
    
    is_busy = user_info[1]
    
    if is_busy:
        try:
            bot.delete_message(chat_id=chat_id, message_id=message.id)
        except:
            pass

    else:
        functions.set_busy(user_id, True)

        history = eval(user_info[0])

        reply_message = bot.send_message(chat_id=chat_id,
                                            text=text.AWAIT,
                                            )
        
        functions.update_message_id(user_id, reply_message.id)

        threading.Thread(daemon=True, 
                        target=functions.connect_ai, 
                        args=(reply_message.id,
                                message.text,
                                message.id,
                                history,
                                user_id,
                                ),
                        ).start()
            

@bot.message_handler(content_types=['audio', 'photo', 'voice', 'video', 'document', 'location', 'contact', 'sticker'])
def handle_text(message):
    bot.send_message(chat_id=message.chat.id,
                     text=text.WRONG_FORMAT,
                     )


if __name__ == '__main__':
    # bot.polling(timeout=80)
    while True:
        try:
            bot.polling()
        except:
            pass

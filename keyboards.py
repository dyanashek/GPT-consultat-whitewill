from telebot import types

import config


def vote_keyboard():
    """Generates keyboard with manager button."""

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('👍', callback_data= 'good'), types.InlineKeyboardButton('👎', callback_data= 'bad'))

    return keyboard
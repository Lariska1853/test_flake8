from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from lexicon.lexicon import LEXICON


def yes_no_keyboard() -> InlineKeyboardMarkup:
    yes = InlineKeyboardButton(text=LEXICON["yes"], callback_data='1')
    no = InlineKeyboardButton(text=LEXICON["no"], callback_data='0')
    keyboard: list[list[InlineKeyboardButton]] = [[yes, no]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def ask_bid_keyboard() -> InlineKeyboardMarkup:
    ask = InlineKeyboardButton(text=LEXICON["ask"], callback_data="ask")
    bid = InlineKeyboardButton(text=LEXICON["bid"], callback_data="bid")
    keyboard: list[list[InlineKeyboardButton]] = [[ask, bid]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

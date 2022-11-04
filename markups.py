from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config as cfg


btnUrlChannel = InlineKeyboardButton(text="Перейти в бот", url=cfg.BOT_URL)
channelMenu = InlineKeyboardMarkup(row_width=1)
channelMenu.insert(btnUrlChannel)

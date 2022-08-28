import logging

from aiogram import Bot, Dispatcher, executor, types

import config as cfg
import markups as nav
from db import Database

logging.basicConfig(level=logging.INFO)

bot = Bot(token=cfg.TOKEN)
dp = Dispatcher(bot)
db = Database('database.db')


def check_sub_channel(chat_member):
    return chat_member['status'] != "left"


@dp.message_handler(commands=['start'], commands_prefix="/")
async def start(message: types.Message):
    await message.reply("Привет!\nИнструкция по использованию бота:\n\
1️⃣ Добавьте бота в канал со всеми правами администратора;\n2️⃣ Добавьте бота в чаты со всеми правами администратора;\n\
Бот подключён. Теперь новые участники чата смогут в нем писать сообщения только после подписки на необходимый канал.\n\
Бот будет проверять подписан ли человек на ваш канал! Если нет - бот не даст ему написать в чат."
                        )


@dp.message_handler(content_types=["new_chat_members"])
async def user_joined(message: types.Message):
    await message.answer(f"{message.from_user.first_name},приветствую тебя!\nЧтобы иметь возможность писать в чат,\
    необходимо подписаться на канал @moy_chanal.", reply_markup=nav.channelMenu)
    if not db.user_exists(message.from_user.id):
        db.add_user(message.from_user.id)
    mute_min = 3600
    return db.add_mute(message.from_user.id, mute_min)


@dp.message_handler()
async def mess_handler(message: types.Message):
    if not db.mute(message.from_user.id):
        return
    else:
        if check_sub_channel(await bot.get_chat_member(chat_id=cfg.CHANNEL_ID, user_id=message.from_user.id)):
            db.mute_del(message.from_user.id, 0)
        else:
            await message.delete()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

# Инструкция по использованию нашего БЕСПЛАТНОГО бота:
# 1️⃣ Добавьте бота в ваш канал со всеми правами администратора;
# 2️⃣ Добавьте бота в ваш чат со всеми правами администратора;
# 3️⃣ Отправьте от имени админа (не анонимно и не от имени чата!!!) в ваш чат команду
# /block Название_канала (пример:
#  /block @reklama_chats);
# 4️⃣Бот подключён. Теперь новые участники чата смогут в нем писать сообщения только после подписки на необходимый канал.
# Бот будет проверять подписан ли человек на ваш канал! Если нет - бот не даст ему написать в чат.
# 5️⃣Для вызова бота в чате можно отправить
# /start @lyuda_2_bot
# 6️⃣Доступные только администратору чата команды:
#
# 1./block [название канала] - включает автоматическую блокировку членов группы, не подписанных на указанный канал
# 2. /unblock [название канала]- отключает автоматическую блокировку пользователей чата, не подписанных на указанный канал

import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from contextlib import suppress

import config as cfg
import markups as nav
from db import Database
from aiogram.utils.exceptions import (MessageCantBeDeleted, MessageToDeleteNotFound)

logging.basicConfig(level=logging.INFO)

bot = Bot(token=cfg.TOKEN)
dp = Dispatcher(bot)
db = Database('database.db')


async def delete_message(message: types.Message, sleep_time: int = 0):
    await asyncio.sleep(sleep_time)
    with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
        await message.delete()


def check_sub_channel(chat_member):
    return chat_member['status'] != "left"


def checking_access_rights(chat_member):
    return chat_member['status'] == "administrator" or chat_member['status'] == "creator"


@dp.message_handler(commands=['start'], commands_prefix="/")
async def start(message: types.Message):
    asyncio.create_task(delete_message(message, 5))
    if message.text[7:] == "@lyuda_2_bot":
        message_answer = await message.answer("Наш БЕСПЛАТНЫЙ бот для вашего бизнеса", reply_markup=nav.channelMenu)
        asyncio.create_task(delete_message(message_answer, 120))
    if message.chat.id == cfg.BOT_ID:
        await message.answer("Привет!\nИнструкция по использованию нашего БЕСПЛАТНОГО бота:\n\
1️⃣ Добавьте бота в ваш канал со всеми правами администратора;\n2️⃣ Добавьте бота в ваш чат со всеми правами администратора;\n\
3️⃣ Отправьте от имени админа (не анонимно и не от имени чата!!!) в ваш чат команду \n/block Название_канала (пример:\n\
 /block @reklama_chats);\n4️⃣Бот подключён. Теперь новые участники чата смогут в нем писать сообщения только после подписки на необходимый канал.\n\
Бот будет проверять подписан ли человек на ваш канал! Если нет - бот не даст ему написать в чат.\n5️⃣Для вызова бота в чате можно отправить\n\
/start @lyuda_2_bot\n6️⃣Доступные только администратору чата команды:\n\n\
1./block [название канала] - включает автоматическую блокировку членов группы, не подписанных на указанный канал\n2. /unblock [название канала]\
- отключает автоматическую блокировку пользователей чата, не подписанных на указанный канал"
                            )


@dp.message_handler(commands=['unblock'], commands_prefix="/")
async def unblock(message: types.Message):
    if checking_access_rights(await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)):
        if db.chat_exists(message.chat.id):
            db.unblock_channel(int(message.chat.id))
        asyncio.create_task(delete_message(message, 5))
        new_msg = await message.reply("Бот деативирован.")
        asyncio.create_task(delete_message(new_msg, 5))


@dp.message_handler(commands=['block'], commands_prefix="/")
async def block(message: types.Message):
    if checking_access_rights(await bot.get_chat_member(chat_id=message.chat.id, user_id=message.from_user.id)):
        if not db.chat_exists(message.chat.id):
            db.add_chat_channel(int(message.chat.id), message.text[7:])
        else:
            db.update_channel(int(message.chat.id), message.text[7:])
        asyncio.create_task(delete_message(message, 10))
        new_msg = await message.reply(f"Бот активирован в чате для канала {message.text[7:]}")
        asyncio.create_task(delete_message(new_msg, 10))


@dp.message_handler(content_types=["new_chat_members"])
async def user_joined(message):
    message_id = await message.answer(f"{message.new_chat_members[0].first_name}, приветствую тебя!\nЧтобы иметь возможность писать в чат,\
    необходимо подписаться на канал {db.receive_channel_url(message.chat.id)}")
    if not db.user_exists(message.new_chat_members[0].id):
        db.add_user(message.new_chat_members[0].id, message.new_chat_members[0].username)
    mute_min = 3600
    db.add_mute(message.new_chat_members[0].id, mute_min)
    asyncio.create_task(delete_message(message_id, 60))


@dp.message_handler()
async def mess_handler(message: types.Message):
    if not db.mute(message.from_user.id):
        return
    else:
        if check_sub_channel(await bot.get_chat_member(chat_id=db.receive_channel_url(message.chat.id), user_id=message.from_user.id)):
            db.mute_del(message.from_user.id, 0)
        else:
            await message.delete()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
import asyncio
import logging
from config_reader import config
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters.command import Command
from aiogram.enums.dice_emoji import DiceEmoji
from db import BotDatabase
from user_agent import get_joke
# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(filename='logs.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# Объект бота
bot = Bot(token=config.BOT_TOKEN.get_secret_value())
# Диспетчер
dp = Dispatcher()
#База данных бота
db = BotDatabase('database.db')

# Хэндлер на команду /start
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer('Start')
    
@dp.message(Command("in"))
async def in_command(message: types.Message):
    chat_id = message.chat.id
    user = message.from_user
    logging.info('/in called, chat_id=%s user_id=%s', chat_id, user.id)
    user_name = user.username or user.first_name or 'anonymous'
    db.add_user(user.id, user_name)
    db.add_user_to_chat(chat_id, user.id)
    await message.reply('Thanks for opting in')
    
@dp.message(Command("out"))
async def out_command(message: types.Message):
    chat_id = message.chat.id
    user = message.from_user
    db.delete_user_from_chat(chat_id, user.id)
    await message.reply('You\'ve been opted out')
    
@dp.message(Command("all"))
async def all_command(message: types.Message):
    chat_id = message.chat.id
    user_list = db.get_users_from_chat(chat_id)
    logging.info('/all called, chat_id=%s user_count=%s', chat_id, len(user_list))
    if not user_list:
        message = 'There are no users. To opt in type /in command'
        await message.reply(text=message)
    else:
        mentions = [mention_markdown(user_id, user_name)
                    for user_id, user_name in user_list]
        
        await message.answer(text=str(mentions), parse_mode=ParseMode.MARKDOWN_V2)
        
def mention_markdown(user_id, user_name):
    return "["+user_name+"](tg://user?id="+str(user_id)+")"
    
@dp.message(Command("stats"))
async def stats_command(message: types.Message):
    reply = f'users: {db.count_users()[0]}\n' \
              f'chats: {db.count_chats()[0]}\n' \
              f'groups: {db.count_groups()[0]}'
    await message.answer(text=reply)
    
@dp.message(Command("dice"))
async def cmd_dice(message: types.Message, bot: Bot):
    await bot.send_dice(message.chat.id, emoji=DiceEmoji.DICE)

@dp.message(Command("joke"))
async def joke_command(message: types.Message, bot: Bot):
    reply = get_joke()
    await message.answer(text=reply)

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
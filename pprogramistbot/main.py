# Standard library imports

# Third party imports
import asyncio
from aiogram import executor
from aiogram.bot import Bot
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher import Dispatcher
from sqlalchemy import insert, update
from aiogram.types import Message, CallbackQuery, ParseMode
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uvloop

# Local application imports
from buttons.inlines_buttons import Languages, MainMenu
from configs import constants, states, subfunctions
from database.models import Reception
from database.settings import engine


uvloop.install()
loop = asyncio.get_event_loop()

bot = Bot(constants.PPROGRAMISTBOT_TOKEN,loop=loop)
storage = RedisStorage2(
    host='localhost',
    db=1,
    # password=constants.REDIS_PASSWORD
)
dp = Dispatcher(bot=bot,loop=loop, storage=storage)


@dp.message_handler(commands=['start'], state='*')
async def start(message: Message):
    await message.answer(
        text=constants.SPEECH_RU["choose_language"],
        reply_markup=Languages().lang_buttons(),
        parse_mode=ParseMode.MARKDOWN
    )

    return await states.BotStates.set_language.set()


@dp.callback_query_handler(state=states.BotStates.set_language)
async def send_main_menu(call: CallbackQuery):
    if call.data == 'ru':
        SPEECH = constants.SPEECH_RU
    else:
        SPEECH = constants.SPEECH_KG

    await call.message.answer(
        text=SPEECH["main_menu"],
        reply_markup=MainMenu(call.data).main_menu_buttons(),
        parse_mode=ParseMode.MARKDOWN
    )

    return await states.BotStates.main_menu.set()



@dp.callback_query_handler(state='*')#state=states.BotStates.main_menu)
async def reception(call: CallbackQuery):
    if call.data:
        async with AsyncSession(engine, future=True) as session:
            await subfunctions.increment_at_reception(
                call, session, 
                Reception, 
                operations={
                    'select': select, 
                    'update': update
                }
            )
        if call.data == 'apply':
            await call.message.answer(
                
            )


if __name__ == "__main__":
    executor.start_polling(
        dispatcher=dp,
        loop=loop
    )
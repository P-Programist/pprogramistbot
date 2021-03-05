import uvloop
from configs import constants
from aiogram import executor
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import Dispatcher
from aiogram.bot import Bot

uvloop.install()

bot = Bot(constants.PPROGRAMISTBOT_TOKEN)


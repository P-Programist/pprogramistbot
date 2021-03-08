from aiogram.dispatcher.filters.state import StatesGroup, State

class BotStates(StatesGroup):
    set_language = State()
    main_menu = State()
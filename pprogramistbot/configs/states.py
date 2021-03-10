from aiogram.dispatcher.filters.state import StatesGroup, State

class BotStates(StatesGroup):
    set_language = State()
    main_menu = State()

    apply_for_course = State()
    set_course_time = State()
    confirm_number_for_applying = State()

    know_about_corses = State()
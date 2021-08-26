from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from configs.constants import SPEECH
from configs.core import redworker


class Languages(object):
    """Languages class is responsible for generating buttons for choosing language."""
    def __init__(self):
        super(Languages, self).__init__()
        self.markup = InlineKeyboardMarkup(row_width=2)

    def lang_buttons(self):
        ru_btn = InlineKeyboardButton(
            'Русский 🇷🇺',
            callback_data='ru'
        )

        kg_btn = InlineKeyboardButton(
            'English 🇱🇷',
            callback_data='kg'
        )

        self.markup.add(ru_btn, kg_btn)

        return self.markup


class MainMenu(object):
    """docstring for MainMenu."""
    def __init__(self, chat_id):
        super(MainMenu, self).__init__()
        self.markup = InlineKeyboardMarkup(row_width=2)

        self.chat_id = chat_id


    async def main_menu_buttons(self, shows):
        lang = await redworker.get_data(chat=self.chat_id)

        apply_btn = InlineKeyboardButton(
            text=SPEECH["apply" + lang],
            callback_data='apply'
        )

        about_courses = InlineKeyboardButton(
            text=SPEECH["about_courses" + lang],
            callback_data='about_courses'
        )

        about_company = InlineKeyboardButton(
            text=SPEECH["about_company_btn" + lang],
            callback_data='about_company'
        )

        vacancies = InlineKeyboardButton(
            text=SPEECH["vacancies" + lang],
            callback_data='vacancies'
        )

        news = InlineKeyboardButton(
            text=SPEECH["news" + lang],
            callback_data='news'
        )

        self.markup.add(apply_btn, about_courses, about_company, vacancies)
        if shows == True:
            self.markup.add(news)

        return self.markup


    async def step_back(self):
        lang = await redworker.get_data(chat=self.chat_id)

        markup = InlineKeyboardMarkup(row_width=2)

        back = InlineKeyboardButton(
            text=SPEECH["back" + lang],
            callback_data='back'
        )

        markup.add(back)

        return markup


class Departments(object):
    """docstring for Departments."""
    def __init__(self, chat_id):
        super(Departments, self).__init__()
        self.chat_id = chat_id
        self.markup = InlineKeyboardMarkup(row_width=1)

    async def departments_buttons(self, back=False):
        lang = await redworker.get_data(chat=self.chat_id)

        python = InlineKeyboardButton(
            text='Python 🐍',
            callback_data='python'
        )
        
        sys_admin = InlineKeyboardButton(
            text='Системный администратор ⚙️',
            callback_data='system_administrator'
        )

        javascript = InlineKeyboardButton(
            text='JavaScript 👨‍🎨',
            callback_data='javascript'
        )

        java = InlineKeyboardButton(
            text='Java ⚒',
            callback_data='java'
        )

        back_btn = InlineKeyboardButton(
            text=SPEECH["back" + lang],
            callback_data='back_to_menu'
        )


        self.markup.add(
            python, sys_admin,
            javascript, java,
        )

        if back:
            self.markup.add(back_btn)

        return self.markup


class GroupTime(object):
    """docstring for GroupTime."""
    def __init__(self, chat_id):
        super(GroupTime, self).__init__()

        self.chat_id = chat_id
        self.markup = InlineKeyboardMarkup(row_width=2)


    async def group_time_buttons(self):
        lang = await redworker.get_data(chat=self.chat_id)

        morning = InlineKeyboardButton(
            text=SPEECH["morning_group" + lang],
            callback_data=0
        )

        evening = InlineKeyboardButton(
            text=SPEECH["evening_group" + lang],
            callback_data=1
        )

        self.markup.add(morning, evening)

        return self.markup



class ActiveVacancies(object):
    def __init__(self, chat_id):
        super(ActiveVacancies, self).__init__()
        self.chat_id = chat_id
            

    async def vacancies(self):
        markup = InlineKeyboardMarkup(row_width=1)
        lang = await redworker.get_data(chat=self.chat_id)

        company = InlineKeyboardButton(
            text=SPEECH["company_vacancies" + lang],
            callback_data='company'
        )


        city = InlineKeyboardButton(
            text=SPEECH["city_vacancies" + lang],
            callback_data='city'
        )

        foreign = InlineKeyboardButton(
            text=SPEECH["foreign_vacancies" + lang],
            callback_data='foreign'
        )

        back_btn = InlineKeyboardButton(
            text=SPEECH["back" + lang],
            callback_data='back_to_menu'
        )

        markup.add(
            company, city, 
            foreign, back_btn
        )

        return markup


    async def apply_for_vacancy(self, vacancy_id):
        markup = InlineKeyboardMarkup(row_width=1)
        lang = await redworker.get_data(chat=self.chat_id)

        apply = InlineKeyboardButton(
            text=SPEECH["apply_for_vacancy" + lang],
            callback_data=vacancy_id
        )

        markup.add(apply)

        return markup

class Departments_type(object):
    """docstring for Departments_type."""
    def __init__(self, chat_id):
        super(Departments_type, self).__init__()
        self.chat_id = chat_id
        self.markup = InlineKeyboardMarkup(row_width=2)

    async def departments_buttons(self, back=False):
        lang = await redworker.get_data(chat=self.chat_id)

        python = InlineKeyboardButton(
            text='Python 🐍',
            callback_data='python2'
        )
        
        javascript = InlineKeyboardButton(
            text='JavaScript 👨‍🎨',
            callback_data='javascript2'
        )

        back = InlineKeyboardButton(
            text=SPEECH["back" + lang],
            callback_data='back'
        )

        self.markup.add(python, javascript, back)


        return self.markup

class Group_time_fb(object):
    """docstring for Group_time_fb."""
    def __init__(self, chat_id):
        super(Group_time_fb, self).__init__()
        self.chat_id = chat_id
        self.markup = InlineKeyboardMarkup(row_width=2)

    async def group_times(self, back=False):
        lang = await redworker.get_data(chat=self.chat_id)

        morning = InlineKeyboardButton(
            text=SPEECH["morning_group" + lang],
            callback_data=0
        )

        evening = InlineKeyboardButton(
            text=SPEECH["evening_group" + lang],
            callback_data=1
        )

        back = InlineKeyboardButton(
            text=SPEECH["back" + lang],
            callback_data='back'
        )

        self.markup.add(morning, evening, back)


        return self.markup
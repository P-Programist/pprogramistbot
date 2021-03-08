from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from configs.constants import SPEECH_KG, SPEECH_RU

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
            'Кыргызча 🇰🇬',
            callback_data='kg'
        )

        self.markup.add(ru_btn, kg_btn)

        return self.markup


class MainMenu(object):
    """docstring for MainMenu."""
    def __init__(self, lang):
        super(MainMenu, self).__init__()
        self.markup = InlineKeyboardMarkup(row_width=2)

        if lang == 'ru':
            self.SPEECH = SPEECH_RU
        else:
            self.SPEECH = SPEECH_KG


    def main_menu_buttons(self):
        apply_btn = InlineKeyboardButton(
            text=self.SPEECH["apply"],
            callback_data='apply'
        )

        about_courses = InlineKeyboardButton(
            text=self.SPEECH["about_courses"],
            callback_data='about_courses'
        )

        about_company = InlineKeyboardButton(
            text=self.SPEECH["about_company"],
            callback_data='about_company'
        )

        vacancies = InlineKeyboardButton(
            text=self.SPEECH["vacancies"],
            callback_data='vacancies'
        )

        news = InlineKeyboardButton(
            text=self.SPEECH["news"],
            callback_data='news'
        )

        self.markup.add(apply_btn, about_courses, about_company, vacancies, news)

        return self.markup


class Departments(object):
    """docstring for Departments."""
    def __init__(self):
        super(Departments, self).__init__()
        self.markup = InlineKeyboardMarkup(row_width=1)

    def departments_buttons(self):
        python = InlineKeyboardButton(
            text='Python',
            callback_data='python'
        )
        
        sys_admin = InlineKeyboardButton(
            text='Системный администратор',
            callback_data='sys_admin'
        )

        javascript = InlineKeyboardButton(
            text='JavaScript',
            callback_data='javascript'
        )

        java = InlineKeyboardButton(
            text='Java',
            callback_data='java'
        )

        self.markup.add(
            python, sys_admin,
            javascript, java
        )

        return self.markup
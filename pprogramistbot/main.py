# Standard library imports

# Third party imports
from aiogram import executor
from aiogram.bot import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.types import Message, CallbackQuery, ParseMode, message
import asyncio
import uvloop

# Local application imports
from buttons.inlines_buttons import (
    Languages, MainMenu, Departments,
    GroupTime
)
from buttons.text_buttons import (
    ConfirmNumber
)
from configs import constants, states, subfunctions
from configs.core import redworker, storage
from database.models import Course, Customer, Reception, Department


uvloop.install()
loop = asyncio.get_event_loop()

bot = Bot(constants.PPROGRAMISTBOT_TOKEN,loop=loop)

dp = Dispatcher(bot=bot,loop=loop, storage=storage)


@dp.message_handler(commands=['start'], state='*')
async def start(message: Message):
    '''
        The first function that the User interacts with.
        After the User pressed the /start command - he will be offered to choose a language for interaction.
    '''

    await message.answer(
        text=constants.SPEECH["choose_language_ru"],
        reply_markup=Languages().lang_buttons(),
        parse_mode=ParseMode.MARKDOWN
    )

    return await states.BotStates.set_language.set()



@dp.callback_query_handler(state=states.BotStates.set_language)
async def send_main_menu(call: CallbackQuery):
    '''
        As soon as User set the most comfortable language,
        we send him buttons of main_menu and change Bot State.
    '''
    chat_id = call.message.chat.id

    if call.data == 'ru':
        await redworker.set_data(chat=chat_id, data='_ru')
    else:
        await redworker.set_data(chat=chat_id, data='_kg')

    lang = await redworker.get_data(chat=chat_id)

    await call.message.edit_text(
        text=constants.SPEECH["main_menu" + lang],
        parse_mode=ParseMode.MARKDOWN
    )
    await call.message.edit_reply_markup(
        reply_markup=await MainMenu(chat_id).main_menu_buttons()
    )

    return await states.BotStates.main_menu.set()



@dp.callback_query_handler(state=states.BotStates.main_menu)
async def reception(call: CallbackQuery):
    '''
        In case, User will be interested to continue,
        the bot will be monitoring which button has been pressed.
        This data is collecting for improving service and watch for users' interests.
    '''
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    if call.data:
        await subfunctions.increment_at_reception(call, Reception)

        if call.data == 'apply':
            await call.message.edit_text(
                text=constants.SPEECH["choose_course" + lang],
                parse_mode=ParseMode.MARKDOWN
            )

            await call.message.edit_reply_markup(
                reply_markup=Departments().departments_buttons()
            )

            return await states.BotStates.apply_for_course.set()


        if call.data == 'about_courses':
            await call.message.edit_text(
                text=constants.SPEECH["choose_course" + lang],
                parse_mode=ParseMode.MARKDOWN
            )

            await call.message.edit_reply_markup(
                reply_markup=Departments().departments_buttons()
            )

            return await states.BotStates.know_about_corses.set()

        if call.data == 'about_company':
            await call.message.edit_text(
                text=constants.SPEECH["choose_course" + lang],
                parse_mode=ParseMode.MARKDOWN
            )

            return await call.message.edit_reply_markup(
                reply_markup=Departments().departments_buttons()
            )

        if call.data == 'vacancies':
            await call.message.edit_text(
                text=constants.SPEECH["choose_course" + lang],
                parse_mode=ParseMode.MARKDOWN
            )

            return await call.message.edit_reply_markup(
                reply_markup=Departments().departments_buttons()
            )

        if call.data == 'news':
            await call.message.edit_text(
                text=constants.SPEECH["choose_course" + lang],
                parse_mode=ParseMode.MARKDOWN
            )

            return await call.message.edit_reply_markup(
                reply_markup=Departments().departments_buttons()
            )


@dp.callback_query_handler(state=states.BotStates.apply_for_course)
async def set_time_for_course(call: CallbackQuery):
    '''
        If the User pressed the "apply" button and wants to apply for a course,
        we find him in the database to see, whether he applied already within the last 3 days.
        This checking is made to avoid people flooding.
        If the User has already applied for a course, he can't apply again for the 3 following days.
        If the User is new we write him into the database to connect to him later.
    '''

    if call.data:

        chat_id = call.message.chat.id
        attr = getattr(Customer, 'chat_id')
        user = await subfunctions.object_exists(attr, chat_id, Customer)
        lang = await redworker.get_data(chat=call.message.chat.id)

        if user:
            if user.phone:
                # If we find the User in database - that means he already applied for the last 3 days
                f_name, dp_name  = user.first_name, user.department_name

                await call.message.edit_text(
                    text=constants.SPEECH["already_applied" + lang].replace('fn', f_name).replace('dp', dp_name),
                    parse_mode=ParseMode.MARKDOWN
                )
                await call.message.answer(
                    text=constants.SPEECH["main_menu" + lang],
                    reply_markup=await MainMenu(chat_id).main_menu_buttons(),
                    parse_mode=ParseMode.MARKDOWN
                )

                return await states.BotStates.main_menu.set()
            else:
                await call.message.edit_text(
                    text=constants.SPEECH["choose_group_time" + lang],
                    reply_markup=await GroupTime(chat_id).group_time_buttons(),
                    parse_mode=ParseMode.MARKDOWN
                )

                return await states.BotStates.set_course_time.set()
        else:
            '''
                The function below is located in "configs.subfunctions" module.
                This function is responsible for operating user's applications for courses.
            '''
            await subfunctions.accept_application(Customer, call)

            await call.message.edit_text(
                    text=constants.SPEECH["choose_group_time" + lang],
                    reply_markup=await GroupTime(chat_id).group_time_buttons(),
                    parse_mode=ParseMode.MARKDOWN
                )

            return await states.BotStates.set_course_time.set()


@dp.callback_query_handler(state=states.BotStates.set_course_time)
async def confirm_number_to_apply(call: CallbackQuery):
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    if call.data and call.data.isdigit():
        attr = getattr(Customer, 'chat_id')
        user = await subfunctions.object_exists(attr, chat_id, Customer)
        await subfunctions.update_object(Customer, user.id, {"time": int(call.data)})

        await call.message.edit_text(
            text=constants.SPEECH["confirm_to_apply" + lang],
            parse_mode=ParseMode.MARKDOWN
        )

        await call.message.answer(
            text=constants.SPEECH["confirm_number_text" + lang],
            reply_markup=await ConfirmNumber(chat_id).confirm_number(),
            parse_mode=ParseMode.MARKDOWN
        )

        return await states.BotStates.confirm_number_for_applying.set()



@dp.message_handler(content_types=['text', 'contact'], state=states.BotStates.confirm_number_for_applying)
async def complete_applying(message: Message):
    chat_id = message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    if message.contact:
        attr = getattr(Customer, 'chat_id')
        user = await subfunctions.object_exists(attr, chat_id, Customer)

        # In case if there will be some symbols other than digits we need to filter them
        await subfunctions.update_object(Customer, user.id, {
            "phone": int(
                            ''.join(
                                [i for i in message.contact.phone_number if i.isdigit()]
                            )
                    )
            }
        )

        await message.answer(
            text=constants.SPEECH["apllication_accepted" + lang],
            parse_mode=ParseMode.MARKDOWN
        )

        with open(constants.WELCOME_TO_THE_CLUB_BUDDY, 'rb') as video:
            await message.answer_video(
                video=video
            )

        await message.answer(
            text=constants.SPEECH["main_menu" + lang],
            reply_markup=await MainMenu(chat_id).main_menu_buttons(),
            parse_mode=ParseMode.MARKDOWN
        )

        return await states.BotStates.main_menu.set()
    else:
        await message.answer(
            text=constants.SPEECH["confirm_number_text" + lang],
            reply_markup=await ConfirmNumber(chat_id).confirm_number(ext=True),
            parse_mode=ParseMode.MARKDOWN
        )

        return await states.BotStates.confirm_number_for_applying.set()


@dp.callback_query_handler(state=states.BotStates.know_about_corses)
async def send_information_about_course(call: CallbackQuery):
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    if call.data:
        # Get an attrubute of Department model
        dp_field = getattr(Department, 'department_name')

        # Edit callback_data into database value
        dp_name = ' '.join(call.data.split('_')).title()

        # Retrieve department object from database by "department_name" 
        dp = await subfunctions.object_exists(dp_field, dp_name, Department)

        # Get an attrubute of Course model
        course_field = getattr(Course, 'department_id')
    
        # Here might be an ERROR in case if database will be empty
        # Retrieve course object from database by "department_id"

        course = await subfunctions.object_exists(course_field, dp.id, Course)

        if not course:
            await call.message.edit_text(
                text=constants.SPEECH["course_under_development" + lang],
                reply_markup=await MainMenu(chat_id).main_menu_buttons(),
                parse_mode=ParseMode.MARKDOWN
            )

            return await states.BotStates.main_menu.set()
        
        await call.message.edit_text(
                text=course.department_info,
                parse_mode=ParseMode.MARKDOWN
            )

        return await states.BotStates.main_menu.set()



if __name__ == "__main__":
    executor.start_polling(
        dispatcher=dp,
        loop=loop
    )
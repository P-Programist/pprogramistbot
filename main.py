# Standard library imports
from datetime import datetime 

# Third party imports
from aiogram import executor
from aiogram.bot import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.types import Message, CallbackQuery, ParseMode, message
import asyncio
from asyncio.tasks import sleep
import uvloop

#SQL Alchemy
from sqlalchemy import update, insert
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

# Local application imports
from buttons.inlines_buttons import (
    Languages,
    MainMenu,
    Departments,
    GroupTime,
    ActiveVacancies,
    DepartmentFeedback,
    FeedbackSchedule,
    Test,
)
from buttons.text_buttons import ConfirmNumber
from configs import constants, states, subfunctions
from configs.core import redworker, storage, point, question, check, time_trecker
from database.settings import engine
from database.models import (
    Course,
    Customer,
    Reception,
    Department,
    Vacancy,
    VacancyApplicants,
    TestQuestions,
)

student_vr = ('1624089338')

uvloop.install()
loop = asyncio.get_event_loop()

bot = Bot(constants.PPROGRAMISTBOT_TOKEN, loop=loop)

dp = Dispatcher(bot=bot, loop=loop, storage=storage)


@dp.message_handler(commands=["start"], state="*")
async def start(message: Message):
    """
    The first function that the User interacts with.
    After the User pressed the /start command - he will be offered to choose a language for interaction.
    """

    await message.answer(
        text=f'{constants.SPEECH["choose_language_ru"]} | {constants.SPEECH["choose_language_kg"]}',
        reply_markup=Languages().lang_buttons(),
        parse_mode=ParseMode.MARKDOWN,
    )

    return await states.BotStates.set_language.set()


@dp.callback_query_handler(state=states.BotStates.set_language)
async def send_main_menu(call: CallbackQuery):
    """
    As soon as User set the most comfortable language,
    we send him buttons of main_menu and change Bot State.
    """
    chat_id = call.message.chat.id

    if call.data == "ru":
        await redworker.set_data(chat=chat_id, data="_ru")
    else:
        await redworker.set_data(chat=chat_id, data="_kg")

    lang = await redworker.get_data(chat=chat_id)

    await call.message.edit_text(
        text=constants.SPEECH["main_menu" + lang],
        reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
        parse_mode=ParseMode.MARKDOWN,
    )

    return await states.BotStates.main_menu.set()


############################################################
######################## RECEPTION #########################
############################################################
@dp.callback_query_handler(state=states.BotStates.main_menu)
async def reception(call: CallbackQuery):
    """
    In case, User will be interested to continue,
    the bot will be monitoring which button has been pressed.
    This data is collecting for improving service and watch for users' interests.
    """
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    if call.data:
        await subfunctions.increment_at_reception(Reception, call)

        if call.data == "apply":
            await call.message.edit_text(
                text=constants.SPEECH["choose_course" + lang],
                reply_markup=await Departments(chat_id).departments_buttons(back=True),
                parse_mode=ParseMode.MARKDOWN,
            )

            return await states.BotStates.apply_for_course.set()

        if call.data == "about_courses":
            await call.message.edit_text(
                text=constants.SPEECH["choose_course" + lang],
                reply_markup=await Departments(chat_id).departments_buttons(back=True),
                parse_mode=ParseMode.MARKDOWN,
            )

            return await states.BotStates.know_about_corses.set()

        if call.data == "about_company":
            reception_id = getattr(Reception, "id")

            reception = await subfunctions.object_exists(Reception, reception_id, 1)

            await call.message.edit_text(
                text=reception.about_company_text,
                reply_markup=await MainMenu(chat_id).step_back(),
                parse_mode=ParseMode.MARKDOWN,
            )

            return await states.BotStates.read_about_company_text.set()

        if call.data == "vacancies":
            await call.message.edit_text(
                text=constants.SPEECH["vacancy_category" + lang],
                reply_markup=await ActiveVacancies(chat_id).vacancies(),
                parse_mode=ParseMode.MARKDOWN,
            )

            return await states.BotStates.vacancy_categories.set()

        if call.data == "feedback":
            await call.message.edit_text(
                # text=constants.SPEECH["not_found" + lang],
                text=constants.SPEECH["changes" + lang],
                reply_markup=await DepartmentFeedback(chat_id).departments_buttons(),
                parse_mode=ParseMode.MARKDOWN,
            )

            return await states.BotStates.add_feedback.set()

        if call.data == "test":
            await call.message.edit_text(
                text=constants.SPEECH["rules" + lang],
                reply_markup=await Test().rules(chat_id),
                parse_mode=ParseMode.MARKDOWN,
            )
            now = datetime.now() 
            await question.set_data(chat=chat_id, data=1)
            await time_trecker.set_data(chat=chat_id, data=now.strftime("%H:%M:%S"))
            await check.set_data(chat=chat_id, data=None)
            await point.set_data(chat=chat_id, data=None)

            return await states.BotStates.start_test.set()


############################################################
###################### END RECEPTION #######################
############################################################


############################################################
####################### APPLICATION ########################
############################################################
@dp.callback_query_handler(state=states.BotStates.apply_for_course)
async def set_time_for_course(call: CallbackQuery):
    """
    If the User pressed the "apply" button and wants to apply for a course,
    we find him in the database to see, whether he applied already within the last 3 days.
    This checking is made to avoid people flooding.
    If the User has already applied for a course, he can't apply again for the 3 following days.
    If the User is new we write him into the database to connect to him later.
    """

    if call.data:

        chat_id = call.message.chat.id
        lang = await redworker.get_data(chat=call.message.chat.id)

        # If User pressed "Back" button - return him to main menu
        if call.data == "back_to_menu":
            await call.message.edit_text(
                text=constants.SPEECH["main_menu" + lang],
                reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
                parse_mode=ParseMode.MARKDOWN,
            )

            return await states.BotStates.main_menu.set()

        attr = getattr(Customer, "chat_id")
        user = await subfunctions.object_exists(Customer, attr, chat_id)

        if user:
            if user.phone:
                # If we find the User in database - that means he already applied for the last 3 days
                f_name, dp_name = user.first_name, user.department_name

                await call.message.edit_text(
                    text=constants.SPEECH["already_applied" + lang]
                    .replace("fn", f_name)
                    .replace("dp", dp_name),
                    parse_mode=ParseMode.MARKDOWN,
                )

                await asyncio.sleep(1.5)

                await call.message.answer(
                    text=constants.SPEECH["main_menu" + lang],
                    reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
                    parse_mode=ParseMode.MARKDOWN,
                )

                return await states.BotStates.main_menu.set()
            else:
                await call.message.edit_text(
                    text=constants.SPEECH["choose_group_time" + lang],
                    reply_markup=await GroupTime(chat_id).group_time_buttons(),
                    parse_mode=ParseMode.MARKDOWN,
                )

                return await states.BotStates.set_course_time.set()
        else:
            """
            The function below is located in "configs.subfunctions" module.
            This function is responsible for operating user's applications for courses.
            """
            department_name = " ".join(call.data.split("_")).title()

            data = {
                "chat_id": chat_id,
                "first_name": call.from_user.first_name,
                "last_name": call.from_user.last_name
                if call.from_user.last_name is not None
                else "Unknown",
                "department_name": department_name,
            }

            await subfunctions.insert_object(Customer, data, call)

            await call.message.edit_text(
                text=constants.SPEECH["choose_group_time" + lang],
                reply_markup=await GroupTime(chat_id).group_time_buttons(),
                parse_mode=ParseMode.MARKDOWN,
            )

            return await states.BotStates.set_course_time.set()


@dp.callback_query_handler(state=states.BotStates.set_course_time)
async def confirm_number_to_apply(call: CallbackQuery):
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    if call.data and call.data.isdigit():
        attr = getattr(Customer, "chat_id")
        user = await subfunctions.object_exists(Customer, attr, chat_id)
        user_id = getattr(Customer, "id")

        await subfunctions.update_object(
            Customer, user_id, user.id, {"time": int(call.data)}
        )

        await call.message.edit_text(
            text=constants.SPEECH["confirm_to_apply" + lang],
            parse_mode=ParseMode.MARKDOWN,
        )

        await call.message.answer(
            text=constants.SPEECH["confirm_number_text" + lang],
            reply_markup=await ConfirmNumber(chat_id).confirm_number(),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.confirm_number_for_applying.set()


@dp.message_handler(
    content_types=["text", "contact"],
    state=states.BotStates.confirm_number_for_applying,
)
async def complete_applying(message: Message):
    chat_id = message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    if message.contact:
        attr = getattr(Customer, "chat_id")
        user = await subfunctions.object_exists(Customer, attr, chat_id)
        user_id = getattr(Customer, "id")

        # In case if there will be some symbols other than digits we need to filter them
        await subfunctions.update_object(
            Customer,
            user_id,
            user.id,
            {
                "phone": int(
                    "".join(
                        [i for i in message.contact.phone_number if i.isdigit()])
                )
            },
        )

        await message.answer(
            text=constants.SPEECH["apllication_accepted" + lang],
            parse_mode=ParseMode.MARKDOWN,
        )

        with open(constants.WELCOME_TO_THE_CLUB_BUDDY, "rb") as video:
            await message.answer_video(video=video)

        await message.answer(
            text=constants.SPEECH["main_menu" + lang],
            reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.main_menu.set()
    else:
        await message.answer(
            text=constants.SPEECH["confirm_number_text" + lang],
            reply_markup=await ConfirmNumber(chat_id).confirm_number(ext=True),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.confirm_number_for_applying.set()


############################################################
##################### END APPLICATION ######################
############################################################


############################################################
###################### ABOUT COURSES #######################
############################################################
@dp.callback_query_handler(state=states.BotStates.know_about_corses)
async def send_information_about_course(call: CallbackQuery):
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    # The condition works when User clicked to the BACK button in the main menu
    if call.data == "back_to_menu":
        await call.message.edit_text(
            text=constants.SPEECH["main_menu" + lang],
            reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.main_menu.set()

    # The condition works when User clicked to the BACK button from Departments
    elif call.data == "back":
        await call.message.edit_text(
            text=constants.SPEECH["choose_course" + lang],
            reply_markup=await Departments(chat_id).departments_buttons(back=True),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.know_about_corses.set()

    if call.data:
        # Get an attrubute of Department model
        dp_field = getattr(Department, "department_name")

        # Edit callback_data into database value
        dp_name = " ".join(call.data.split("_")).title()

        # Retrieve department object from database by "department_name"
        dp = await subfunctions.object_exists(Department, dp_field, dp_name)

        # Get an attrubute of Course model
        course_field = getattr(Course, "department_id")

        # Here might be an ERROR in case if database will be empty
        # Retrieve course object from database by "department_id"
        course = await subfunctions.object_exists(Course, course_field, dp.id)

        if not course:
            await call.message.edit_text(
                text=constants.SPEECH["course_under_development" + lang],
                reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
                parse_mode=ParseMode.MARKDOWN,
            )

            return await states.BotStates.main_menu.set()

        await call.message.edit_text(
            text=course.department_info,
            reply_markup=await MainMenu(chat_id).step_back(),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.know_about_corses.set()


############################################################
#################### END ABOUT COURSES #####################
############################################################


############################################################
###################### ABOUT COMPANY #######################
############################################################
@dp.callback_query_handler(state=states.BotStates.read_about_company_text)
async def read_about_company(call: CallbackQuery):
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    # If User pressed "Back" button - return him to main menu
    if call.data:
        await call.message.edit_text(
            text=constants.SPEECH["main_menu" + lang],
            reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.main_menu.set()


############################################################
#################### END ABOUT COMPANY #####################
############################################################


############################################################
######################## VACANCIES #########################
############################################################
@dp.callback_query_handler(state=states.BotStates.vacancy_categories)
async def vacancy_list(call: CallbackQuery):
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    if call.data == "back_to_menu":
        await call.message.edit_text(
            text=constants.SPEECH["main_menu" + lang],
            reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.main_menu.set()

    vacancies_list = await subfunctions.extract_vacancies(call)

    if not vacancies_list:
        await call.message.answer(
            text=constants.SPEECH["not_found" +
                                  lang], parse_mode=ParseMode.MARKDOWN
        )

        return await states.BotStates.vacancy_categories.set()

    await call.message.delete_reply_markup()

    async for text, button in vacancies_list:
        await call.message.answer(
            text=text, reply_markup=button, parse_mode=ParseMode.MARKDOWN
        )
    else:
        await call.message.answer(
            text=constants.SPEECH["back_to_vacancies" + lang],
            reply_markup=await MainMenu(chat_id).step_back(),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.local_vacancies.set()


@dp.callback_query_handler(state=states.BotStates.local_vacancies)
async def vacancies_list_provided(call: CallbackQuery):
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    if call.data == "back":
        await call.message.edit_text(
            text=constants.SPEECH["vacancy_category" + lang],
            reply_markup=await ActiveVacancies(chat_id).vacancies(),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.vacancy_categories.set()

    chat_id_attr = getattr(VacancyApplicants, "chat_id")
    applicant = await subfunctions.object_exists(
        VacancyApplicants, chat_id_attr, chat_id
    )

    if applicant:
        if applicant.phone_number:
            await call.message.answer(
                text=constants.SPEECH["already_applied_for_vacancy" + lang],
                parse_mode=ParseMode.MARKDOWN,
            )

            await asyncio.sleep(1.5)

            await call.message.answer(
                text=constants.SPEECH["main_menu" + lang],
                reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
                parse_mode=ParseMode.MARKDOWN,
            )

            return await states.BotStates.main_menu.set()

    data = {
        "vacancy_id": int(call.data),
        "chat_id": chat_id,
    }

    await subfunctions.insert_object(VacancyApplicants, data, call)

    await call.message.answer(
        text=constants.SPEECH["tell_me_full_name" +
                              lang], parse_mode=ParseMode.MARKDOWN
    )

    return await states.BotStates.full_name_for_vacancy.set()


@dp.message_handler(
    content_types=["text"], state=states.BotStates.full_name_for_vacancy
)
async def ask_fullname_for_vacancy(message: Message):
    chat_id = message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    chat_id_attr = getattr(VacancyApplicants, "chat_id")
    await subfunctions.update_object(
        VacancyApplicants, chat_id_attr, chat_id, {"full_name": message.text}
    )

    await message.answer(
        text=constants.SPEECH["cover_letter" +
                              lang], parse_mode=ParseMode.MARKDOWN
    )

    return await states.BotStates.cover_letter.set()


@dp.message_handler(content_types=["text"], state=states.BotStates.cover_letter)
async def ask_cover_letter_for_vacancy(message: Message):
    chat_id = message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    chat_id_attr = getattr(VacancyApplicants, "chat_id")
    await subfunctions.update_object(
        VacancyApplicants, chat_id_attr, chat_id, {
            "cover_letter": message.text}
    )

    await message.answer(
        text=constants.SPEECH["provide_github" +
                              lang], parse_mode=ParseMode.MARKDOWN
    )

    return await states.BotStates.github_link.set()


@dp.message_handler(content_types=["text"], state=states.BotStates.github_link)
async def ask_github_link_for_vacancy(message: Message):
    chat_id = message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    if 'github' in message.text or 'bitbucket' in message.text:
        chat_id_attr = getattr(VacancyApplicants, "chat_id")
        await subfunctions.update_object(
            VacancyApplicants, chat_id_attr, chat_id, {
                "github_link": message.text}
        )

        await message.answer(
            text=constants.SPEECH["confirm_to_apply" +
                                  lang], parse_mode=ParseMode.MARKDOWN
        )

        await message.answer(
            text=constants.SPEECH["confirm_number_text" + lang],
            reply_markup=await ConfirmNumber(chat_id).confirm_number(),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.confirm_number_for_vacancy.set()

    else:
        await message.answer(
            text=constants.SPEECH["provide_github" +
                                  lang], parse_mode=ParseMode.MARKDOWN
        )
        return await states.BotStates.github_link.set()


@dp.message_handler(
    content_types=["text", "contact"], state=states.BotStates.confirm_number_for_vacancy
)
async def complete_vacancy_applying(message: Message):
    chat_id = message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    if message.contact:
        chat_id_attr = getattr(VacancyApplicants, "chat_id")
        await subfunctions.update_object(
            VacancyApplicants,
            chat_id_attr,
            chat_id,
            {
                "phone_number": int(
                    "".join(
                        [i for i in message.contact.phone_number if i.isdigit()])
                )
            },
        )

        await message.answer(
            text=constants.SPEECH["apllication_accepted" + lang],
            parse_mode=ParseMode.MARKDOWN,
        )

        await asyncio.sleep(1.7)

        await message.answer(
            text=constants.SPEECH["main_menu" + lang],
            reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.main_menu.set()

    await message.answer(
        text=constants.SPEECH["confirm_to_apply" + lang],
        reply_markup=await ConfirmNumber(chat_id).confirm_number(),
        parse_mode=ParseMode.MARKDOWN,
    )

    return await states.BotStates.confirm_number_for_vacancy.set()


############################################################
###################### END VACANCIES #######################
############################################################

############################################################
######################## FEEDBACKS #########################
############################################################
@dp.callback_query_handler(state=states.BotStates.add_feedback)
async def check_group(call: CallbackQuery):
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    if call.data == "python2":
        await call.message.edit_text(
            text=constants.SPEECH["changes_time" + lang],
            reply_markup=await FeedbackSchedule(chat_id).group_times(),
            parse_mode=ParseMode.MARKDOWN,
        )
    elif call.data == "javascript2":
        await call.message.edit_text(
            text=constants.SPEECH["changes_time" + lang],
            reply_markup=await FeedbackSchedule(chat_id).group_times(),
            parse_mode=ParseMode.MARKDOWN,
        )
    elif call.data == "back":
        await call.message.edit_text(
            text=constants.SPEECH["main_menu" + lang],
            reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
            parse_mode=ParseMode.MARKDOWN,
        )

        return await states.BotStates.main_menu.set()
    return await states.BotStates.choose_times.set()


@dp.callback_query_handler(state=states.BotStates.choose_times)
async def choose_times_gr(call: CallbackQuery):
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    if call.data == "0":
        await call.message.edit_text(
            text=constants.SPEECH["feedback" + lang],
            parse_mode=ParseMode.MARKDOWN,
        )
    elif call.data == "1":
        await call.message.edit_text(
            text=constants.SPEECH["feedback" + lang],
            parse_mode=ParseMode.MARKDOWN,
        )

    return await states.BotStates.feedback_text.set()


@dp.message_handler(content_types=["text"], state=states.BotStates.feedback_text)
async def feedback_text(message: Message):
    chat_id = message.chat.id
    lang = await redworker.get_data(chat=chat_id)

    # print(message.text)

    await message.answer(
        text=constants.SPEECH["main_menu" + lang],
        reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
        parse_mode=ParseMode.MARKDOWN,
    )
    return await states.BotStates.main_menu.set()

############################################################
###################### END FEEDBACKS #######################
############################################################

############################################################
########################## TESTS ###########################
############################################################


@dp.callback_query_handler(state=states.BotStates.start_test)
async def questions(call: CallbackQuery):
    '''В этой функции отправляются вопросы и записываются в БД ответы пользователей, 
    далее отправляет это данные в следущую функцию.'''
    
    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)
    question_id = await question.get_data(chat=chat_id)
    checking = await check.get_data(chat=chat_id)
    time_treck = await time_trecker.get_data(chat=chat_id)

    if call.data == "back" or call.data == "stop_test":
        await call.message.edit_text(
            text=constants.SPEECH["main_menu" + lang],
            reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
            parse_mode=ParseMode.MARKDOWN,
        )
        return await states.BotStates.main_menu.set()

    now = datetime.now() 
    current_time = now.strftime("%H:%M:%S") 
    times = str(datetime.strptime(current_time, constants.TYPE_TIME) - datetime.strptime(time_treck, constants.TYPE_TIME))

    if datetime.strptime(times, constants.TYPE_TIME) > datetime.strptime(constants.TIME_LIMIT, constants.TYPE_TIME):
        await call.message.edit_text(
            text=f'{constants.SPEECH["time_stop" + lang]} \n{constants.SPEECH["main_menu" + lang]}',
            reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
            parse_mode=ParseMode.MARKDOWN,
        )
        return await states.BotStates.main_menu.set()

    if question_id <= 10:
        questions_list = await subfunctions.questions(call, question_id)
        generat = next(questions_list)

        if not call.data == 'start_test':
            if checking:
                await check.set_data(chat=chat_id, data=f'{checking}, {call.data}')
            else:
                await check.set_data(chat=chat_id, data=f'{call.data}')

        await call.message.edit_text(
            text=generat[0],
            reply_markup=await Test().choose_true_answers(chat_id, generat[1].split(', ')),
            parse_mode=ParseMode.MARKDOWN
        )
        await question.set_data(chat=chat_id, data=1+question_id)
    else:
        await check.set_data(chat=chat_id, data=f'{checking}, {call.data}')

        await call.message.edit_text(
            text=constants.SPEECH["know_point" + lang],
            reply_markup=await Test().know_points(chat_id),
            parse_mode=ParseMode.MARKDOWN,
        )
        return await states.BotStates.choose_answer.set()

    return await states.BotStates.start_test.set()

@dp.callback_query_handler(state=states.BotStates.choose_answer)
async def questions(call: CallbackQuery):
    '''В этой функции проверяется правильно ли он ответил на тот или иной вопрос, 
    далее все баллы подсчитиваютя и отправляются пользователю.'''

    chat_id = call.message.chat.id
    lang = await redworker.get_data(chat=chat_id)
    checking = await check.get_data(chat=chat_id)

    if call.data == 'knows':
        for question_id in range(1, 11):
            questions_list = await subfunctions.questions(call, question_id)
            generat = next(questions_list)
            if generat[2] == checking.split(', ')[question_id-1]:
                points = await point.get_data(chat=chat_id)
                if points:
                    await point.set_data(chat=chat_id, data=points+generat[3])
                else:
                    await point.set_data(chat=chat_id, data=generat[3])
                
    
    await call.message.edit_text(
        text=f'Ваш результат: {await point.get_data(chat=chat_id)} баллов! \n{constants.SPEECH["main_menu" + lang]}',
        reply_markup=await MainMenu(chat_id).main_menu_buttons(str(chat_id) in student_vr),
        parse_mode=ParseMode.MARKDOWN,
    )
    return await states.BotStates.main_menu.set()



############################################################
######################## END TESTS #########################
############################################################

if __name__ == "__main__":
    executor.start_polling(dispatcher=dp, loop=loop)


from sqlalchemy import update, insert
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.inlines_buttons import ActiveVacancies
from database.models import Vacancy, TestQuestions
from database.settings import engine


async def increment_at_reception(model, call):
    # Only one operation under sessionb.begin() is allowed.
        # If You want make one more request to Database,
        # just make with session.execute().
    async with AsyncSession(engine) as session:
        async with session.begin():

            # After we get "callback_data" value we extract the same attribute from Reception object,
                # as the callback_data and attribute have the same names.
            attr = getattr(model, call.data)

            applies = select(attr)
            request = await session.execute(applies)

            clicks = request.scalars().first()

            # We can update values by passing them as a dictionary
            incrementation = update(model).values({call.data: clicks+1})
            await session.execute(incrementation)
            



async def object_exists(model, attr_name, attr_value, *args):
    # "expire_on_commit" allows to continue to store data even after the session is closed.
    # So as we use Context Manager the session will be closed in any case.
    async with AsyncSession(engine, expire_on_commit=False) as session:

        # Do not call "session.commit()" in case you write "session.begin()"
        async with session.begin():
            if args:
                if args[0][2] == 'and':
                    find_object_query = select(model).where(attr_name == attr_value and args[0][0] == args[0][1])
                else:
                    find_object_query = select(model).where(attr_name == attr_value or args[0][0] == args[0][1])
            else:
                find_object_query = select(model).where(attr_name == attr_value)
            result = await session.execute(find_object_query)
            obj = result.scalar()

    return obj if obj else []



async def insert_object(model, data, call):
    request = insert(model).values(data)

    async with AsyncSession(engine) as session:
        # Do not call "session.commit()" in case you write "session.begin()"
        async with session.begin():
            await session.execute(request)

    return data


async def update_object(model, object_attr, attr_value, data, *args):
    async with AsyncSession(engine) as session:
        # Do not call "session.commit()" in case you write "session.begin()"
        async with session.begin():
            request = update(model).where(object_attr==attr_value).values(data)

            await session.execute(request)

    return data


async def extract_vacancies(call):
    chat_id = call.message.chat.id

    async with AsyncSession(engine, expire_on_commit=False) as session:
        async with session.begin():
            MAP = {
                "company": 0,
                "city": 1,
                "foreign": 2
            }
            vacancy_list = select(Vacancy).where(
                Vacancy.vacancy_type == MAP[call.data]
            )

            lst = await session.execute(vacancy_list)


    data = lst.all()
    
    if data:
        return (
            (
                item[0].position, await ActiveVacancies(chat_id).apply_for_vacancy(item[0].id)
            ) for item in data
        )

    return data


async def questions(call, question_id):
    chat_id = call.message.chat.id

    async with AsyncSession(engine, expire_on_commit=False) as session:
        async with session.begin():
            question_list = select(TestQuestions).where(
                TestQuestions.id == question_id
            )

            lst = await session.execute(question_list)
    

    data = lst.all()

    if data:
        return (
            (
                item[0].question, item[0].answers, item[0].true_answers, item[0].significance
            ) for item in data
        )

    return data


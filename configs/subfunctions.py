import aiogram
from sqlalchemy import update, insert
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from buttons.inlines_buttons import ActiveVacancies
from database.models import Reception, Vacancy, BishkekVacancy
from database.settings import engine
import asyncio


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
            if not clicks:
                clicks = 0

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
                    find_object_query = select(model).where(
                        attr_name == attr_value and args[0][0] == args[0][1])
                else:
                    find_object_query = select(model).where(
                        attr_name == attr_value or args[0][0] == args[0][1])
            else:
                find_object_query = select(model).where(
                    attr_name == attr_value)
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
            request = update(model).where(
                object_attr == attr_value).values(data)

            await session.execute(request)

    return data


async def extract_our_vacancies(call) -> tuple:
    chat_id = call.message.chat.id

    async with AsyncSession(engine, expire_on_commit=False) as session:
        async with session.begin():
            vacancy_list = select(Vacancy)

            lst = await session.execute(vacancy_list)

    data = lst.all()

    if data:
        return (
            (
                item[0].header, await ActiveVacancies(chat_id).apply_for_vacancy(item[0].id)
            ) for item in data
        )

    return data


async def extract_bishkek_vacancies()->list:
    """
    This function extracts data from the fields specified in «select» and displays the first 10 of them.
    Эта функция извлекает данные из полей, указанных в «select», и отображает первые 10 из них.
    """

    async with AsyncSession(engine, expire_on_commit=False) as session:
        async with session.begin():
            vacancy_list = select(BishkekVacancy.header, BishkekVacancy.salary, BishkekVacancy.details, BishkekVacancy.required_experience, BishkekVacancy.schedule, BishkekVacancy.company_name)

            lst = await session.execute(vacancy_list)

            data = [i for i in lst.fetchall()]

            return data[:10]


async def extract_world_vacancies(call) -> tuple:
    chat_id = call.message.chat.id

    async with AsyncSession(engine, expire_on_commit=False) as session:
        async with session.begin():
            vacancy_list = select(BishkekVacancy)

            lst = await session.execute(vacancy_list)

    data = lst.all()

    if data:
        return (
            (
                item[0].header, await ActiveVacancies(chat_id).apply_for_vacancy(item[0].id)
            ) for item in data
        )

    return data


async def get_stats() -> tuple:

    async with AsyncSession(engine, expire_on_commit=False) as session:
        async with session.begin():

            reception_list = select(Reception)
            lst = await session.execute(reception_list)

            data = lst.fetchone()[0]
            return {"apply": data.apply, "about_company": data.about_company, "about_courses": data.about_courses, "vacancies": data.vacancies}


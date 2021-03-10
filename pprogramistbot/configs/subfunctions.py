from aiogram.types import CallbackQuery, Message
from sqlalchemy import update, insert
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from configs.constants import SPEECH
from configs.core import redworker
from database.settings import engine


async def increment_at_reception(call, model):
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
        if clicks is None:
            session.add(
                model(
                    apply=0, about_courses=0,
                    about_company=0, vacancies=0,
                    news=0
                )
            )
            await session.commit()
        else:
            # We can update values by passing them as a dictionary
            incrementation = update(model).values({call.data: clicks+1})
            await session.execute(incrementation)
            await session.commit()



async def object_exists(attr_name, attr_value, model):
    # "expire_on_commit" allows to continue to store data even after the session is closed.
    # So as we use Context Manager the session will be closed in any case.
    async with AsyncSession(engine, expire_on_commit=False) as session:

        # Do not call "session.commit()" in case you write "session.begin()"
        async with session.begin():
            find_object_query = select(model).where(attr_name == attr_value)
            result = await session.execute(find_object_query)
            obj = result.scalar()

    return obj if obj else []



async def update_object(model, object_id, data):
    async with AsyncSession(engine) as session:
        # Do not call "session.commit()" in case you write "session.begin()"
        async with session.begin():
            request = update(model).where(model.id==object_id).values(data)

            await session.execute(request)

    return data


async def accept_application(model, call):
    chat_id = call.message.chat.id
    department_name = ' '.join(call.data.split('_')).title()
    
    data = {
        "chat_id": chat_id,
        "first_name": call.from_user.first_name,
        "last_name": call.from_user.last_name if call.from_user.last_name is not None else 'Unknown',
        "department_name": department_name
    }

    request = insert(model).values(data)

    async with AsyncSession(engine) as session:
        # Do not call "session.commit()" in case you write "session.begin()"
        async with session.begin():
            await session.execute(request)

    return data

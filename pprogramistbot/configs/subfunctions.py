async def increment_at_reception(call, session, _class, **kwargs):
    # Only one operation under sessionb.begin() is allowed.
        # If You want make one more request to Database,
        # just make with session.execute().
    async with session.begin():

        # After we get "callback_data" value we extract the same attribute from Reception object,
            # as the callback_data and attribute have the same names.
        attr = getattr(_class, call.data)

        applies = kwargs.get('operations').get('select')(attr)
        request = await session.execute(applies)

        clicks = request.scalars().first()
    if clicks is None:
        session.add(
            _class(
                apply=0, about_courses=0,
                about_company=0, vacancies=0,
                news=0
            )
        )
        await session.commit()
    else:
        # We can update values by passing them as a dictionary
        incrementation = kwargs.get('operations').get('update')(_class).values({call.data: clicks+1})
        await session.execute(incrementation)
        await session.commit()

    await session.close()

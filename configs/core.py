from aiogram.contrib.fsm_storage.redis import RedisStorage2

storage = RedisStorage2(
    host='localhost',
    db=1
)

redworker = RedisStorage2(
    host='localhost',
    db=2
)
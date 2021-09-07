from aiogram.contrib.fsm_storage.redis import RedisStorage2
from .constants import REDIS_PASSWORD

storage = RedisStorage2(
    host="127.0.0.1",
    db=1,
    port=6379,
    password=REDIS_PASSWORD,
)

redworker = RedisStorage2(
    host="127.0.0.1",
    db=2,
    port=6379,
    password=REDIS_PASSWORD,
)

point = RedisStorage2(
    host="127.0.0.1",
    db=3,
    port=6379,
    password=REDIS_PASSWORD,
)
'''Таблица point хранит в себе баллы собранные пользователем'''

time_question = RedisStorage2(
    host='127.0.0.1',
    db=4,
    port=6379,
    password=REDIS_PASSWORD,
)
'''Таблица time_question хранит в себе время в которое должен уложиться пользователь во время теста, также на каком вопросе находился пользователь'''

check = RedisStorage2(
    host="127.0.0.1",
    db=5,
    port=6379,
    password=REDIS_PASSWORD,
)
'''Таблица check хранит в себе ответы пользователя'''

feedback_data = RedisStorage2(
    host="127.0.0.1",
    db=6,
    port=6379,
    password=REDIS_PASSWORD,
)
'''Таблица feedback_data хранит в себе данные пользователя, при этом созраняются они по этапно'''
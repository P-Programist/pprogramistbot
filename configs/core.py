from aiogram.contrib.fsm_storage.redis import RedisStorage2
from .constants import REDIS_PASSWORD

storage = RedisStorage2(
    host='localhost',
    db=1,
    password=REDIS_PASSWORD
)

redworker = RedisStorage2(
    host='localhost',
    db=2,
    password=REDIS_PASSWORD
)
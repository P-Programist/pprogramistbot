from aiogram.contrib.fsm_storage.redis import RedisStorage2
from .constants import REDIS_PASSWORD

storage = RedisStorage2(
    host='127.0.0.1',
    db=1,
    port = 6379, 
    password = REDIS_PASSWORD
)

redworker = RedisStorage2(
    host='127.0.0.1',
    db=2,
    port = 6379, 
    password = REDIS_PASSWORD
)
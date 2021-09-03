from aiogram.contrib.fsm_storage.redis import RedisStorage2
from configs.constants import REDIS_PASSWORD

storage = RedisStorage2(
    host='localhost',
    db=1,
    port=6379,
    password=REDIS_PASSWORD
)

redworker = RedisStorage2(
    host='localhost',
    db=2,
    port=6379,
    password=REDIS_PASSWORD
)
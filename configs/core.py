from aiogram.contrib.fsm_storage.redis import RedisStorage2
<<<<<<< HEAD
from .constants import REDIS_PASSWORD
=======
from configs.constants import REDIS_PASSWORD
>>>>>>> 627b56df32d73fd49f3e964434bf7af543f6290b

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
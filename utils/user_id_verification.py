import asyncio
import re
import traceback

import loguru

import config.conf
from services.twitter_services import get_user_twitter_id_by_apidance


async def verify_user_id(user_name: str):
    try:
        # 判断是以@开头
        if user_name.startswith('@'):
            user_name = user_name[1:]

        if not re.fullmatch(r"^[A-Za-z_]+$", user_name):
            return None

        for attempt in range(1, config.conf.settings.MAX_RETRIES + 1):
            try:
                result = await get_user_twitter_id_by_apidance(username=user_name)

                if result is not None:
                    return result
            except Exception as e:
                loguru.logger.error(e)
                loguru.logger.error(traceback.format_exc())
            await asyncio.sleep(config.conf.settings.DELAY)
        return None
    except Exception as e:
        loguru.logger.error(e)
        loguru.logger.error(traceback.format_exc())
        return False


async def main():
    user_name = input("please enter your username: ")
    result = await verify_user_id(user_name)
    print(result)


if __name__ == '__main__':
    asyncio.run(main())

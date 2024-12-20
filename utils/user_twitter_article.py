import asyncio
import traceback

import loguru

import config.conf
from services.data_processing import user_data_processing
from services.twitter_services import get_user_twitter_data_by_apidance


async def get_user_twitter_article(user_id: str):
    try:
        loguru.logger.error(user_id)
        for attempt in range(1, config.conf.settings.MAX_RETRIES + 1):
            try:
                result = await get_user_twitter_data_by_apidance(user_id=user_id)
                loguru.logger.error(result)
                if 'errors' in result:
                    await asyncio.sleep(config.conf.settings.DELAY)
                elif result.get('data').get('user'):
                    data = await user_data_processing(result)
                    print(f"data-------{data}")
                    return data

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
    result = await get_user_twitter_article(user_name)
    print(result)


if __name__ == '__main__':
    asyncio.run(main())

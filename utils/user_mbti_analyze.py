import asyncio
import re
import traceback

import loguru

import config.conf
from services.mbti_analysis import mbti_genai_analysis


async def get_user_mbti_analyze(data, user_name: str):
    try:

        for attempt in range(1, config.conf.settings.MAX_RETRIES + 1):
            try:
                result = await mbti_genai_analysis(data=data, name=user_name)

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
    result = await get_user_mbti_analyze(user_name)
    print(result)


if __name__ == '__main__':
    asyncio.run(main())

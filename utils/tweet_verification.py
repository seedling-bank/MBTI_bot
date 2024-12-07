import asyncio
import json
import traceback

import loguru
import requests

import config.conf
from services.data_processing import user_data_processing
from services.twitter_services import get_user_twitter_data_by_apidance


async def get_tweet_verification(twitter_id):
    try:
        data = None
        try:
            for attempt in range(1, config.conf.settings.MAX_RETRIES + 1):
                try:
                    result = await get_user_twitter_data_by_apidance(user_id=twitter_id)
                    if 'errors' in result:
                        await asyncio.sleep(config.conf.settings.DELAY)
                    elif result.get('data').get('user'):
                        data = await user_data_processing(result)
                        break
                except Exception as e:
                    loguru.logger.error(e)
                    loguru.logger.error(traceback.format_exc())
                await asyncio.sleep(config.conf.settings.DELAY)
                data = None
        except Exception as e:
            loguru.logger.error(e)
            loguru.logger.error(traceback.format_exc())
            data = None
        if data is not None:
            if "Join🪐✨ #MBTIPUMP" in data and '🌌 Application #10233 - MBTI PUMP 🚀' in data:
                return True
            else:
                return False
        else:
            return False

    except Exception as e:
        loguru.logger.error(e)
        loguru.logger.error(traceback.format_exc())
        return False
import asyncio
import json
import traceback
from datetime import datetime

import loguru
from sqlalchemy import update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

import config.conf
from models.user_model import UserModel

engine = create_async_engine(
    config.conf.settings.DATABASE_URI,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800
)

SessionFactory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_user(telegram_id, twitter_id, twitter_username):
    try:
        current_time = datetime.utcnow()
        current_time_s = current_time.strftime("%Y-%m-%d %H:%M:%S")
        current_time_timestamp = int(current_time.timestamp() * 1000)
        async with SessionFactory() as session:

            new_user = UserModel(
                telegram_id=str(telegram_id),
                twitter_id=str(twitter_id),
                twitter_username=str(twitter_username),
                created_at=current_time_s,
                create_time=current_time_timestamp,
                update_time=current_time_timestamp,
                twitter_verified='0'
            )
            session.add(new_user)
            await session.commit()

            user_id = new_user.id

            await session.close()

            return user_id

    except Exception as e:
        loguru.logger.error(e)
        loguru.logger.error(traceback.format_exc())
        return None


async def update_user_twitter(telegram_id, twitter_id, user_tweets):
    try:
        current_time = datetime.utcnow()
        current_time_timestamp = int(current_time.timestamp() * 1000)
        async with SessionFactory() as session:

            user_twitter_stmt = (
                update(UserModel)
                .where(UserModel.telegram_id == telegram_id)
                .where(UserModel.twitter_id == twitter_id)
                .values(
                    user_tweets=user_tweets,
                    update_time=current_time_timestamp
                )
            )
            result = await session.execute(user_twitter_stmt)
            await session.commit()
            await session.close()

            if result.rowcount > 0:
                return True
            else:
                return False

    except Exception as e:
        loguru.logger.error(e)
        loguru.logger.error(traceback.format_exc())
        return False


async def update_user_mbti(telegram_id, twitter_id, user_mbti_analyze, mbti_type):
    try:
        current_time = datetime.utcnow()
        current_time_timestamp = int(current_time.timestamp() * 1000)
        async with SessionFactory() as session:

            user_twitter_stmt = (
                update(UserModel)
                .where(UserModel.telegram_id == telegram_id)
                .where(UserModel.twitter_id == twitter_id)
                .values(
                    user_mbti_analyze=user_mbti_analyze,
                    mbti_type=mbti_type,
                    update_time=current_time_timestamp
                )
            )
            result = await session.execute(user_twitter_stmt)
            await session.commit()
            await session.close()

            if result.rowcount > 0:
                return True
            else:
                return False

    except Exception as e:
        loguru.logger.error(e)
        loguru.logger.error(traceback.format_exc())
        return False


async def update_user_psychological_state(
        telegram_id, twitter_id, psychological_analysis_type, psychological_analysis):
    try:
        current_time = datetime.utcnow()
        current_time_timestamp = int(current_time.timestamp() * 1000)
        async with SessionFactory() as session:

            user_twitter_stmt = (
                update(UserModel)
                .where(UserModel.telegram_id == telegram_id)
                .where(UserModel.twitter_id == twitter_id)
                .values(
                    psychological_analysis_type=psychological_analysis_type,
                    psychological_analysis=json.dumps(psychological_analysis),
                    update_time=current_time_timestamp
                )
            )
            result = await session.execute(user_twitter_stmt)
            await session.commit()
            await session.close()

            if result.rowcount > 0:
                return True
            else:
                return False

    except Exception as e:
        loguru.logger.error(e)
        loguru.logger.error(traceback.format_exc())
        return False


async def update_user_twitter_claim(
        telegram_id, twitter_id):
    try:
        current_time = datetime.utcnow()
        current_time_timestamp = int(current_time.timestamp() * 1000)
        async with SessionFactory() as session:

            user_twitter_stmt = (
                update(UserModel)
                .where(UserModel.telegram_id == telegram_id)
                .where(UserModel.twitter_id == twitter_id)
                .values(
                    twitter_verified="1",
                    update_time=current_time_timestamp
                )
            )
            result = await session.execute(user_twitter_stmt)
            await session.commit()
            await session.close()

            if result.rowcount > 0:
                return True
            else:
                return False

    except Exception as e:
        loguru.logger.error(e)
        loguru.logger.error(traceback.format_exc())
        return False

async def main():
    # telegram_id = 1
    # twitter_id = 2
    # twitter_username = "123"
    # result = await create_user(telegram_id, twitter_id, twitter_username)
    # print(result)

    # telegram_id = 1
    # twitter_id = 2
    # user_tweets = "a"
    # result = await update_user_twitter(telegram_id, twitter_id, user_tweets)
    # print(result)

    telegram_id = 1
    twitter_id = 2
    user_mbti_analyze = "你好啊～"
    mbti_type = "mbti"
    result = await update_user_mbti(telegram_id, twitter_id, user_mbti_analyze, mbti_type)
    print(result)


if __name__ == '__main__':
    asyncio.run(main())

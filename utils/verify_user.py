import asyncio
import traceback
from datetime import datetime

from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, scoped_session
import loguru

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


async def verify_user(telegram_id, twitter_id):
    try:
        async with SessionFactory() as session:

            stmt = select(UserModel).where(
                UserModel.telegram_id == telegram_id,
                UserModel.twitter_id == twitter_id
            )
            result = await session.execute(stmt)
            user_data = result.scalars().first()
        if user_data is not None:
            # 用户存在，返回用户 ID 或其他标识
            return user_data
        else:
            # 用户不存在，返回 None 或其他适当的值
            return None
    except Exception as e:
        loguru.logger.error(e)
        loguru.logger.error(traceback.format_exc())
        return None


async def main():
    telegram_id = 1
    twitter_id = 2
    result = await verify_user(telegram_id=telegram_id, twitter_id=twitter_id)
    print(result.id, type(result.id))
    print(result.twitter_id, type(result.twitter_id))
    print(result.telegram_id, type(result.telegram_id))
    print(result.twitter_username, type(result.twitter_username))
    print(result.user_tweets, type(result.user_tweets))
    print(result.user_mbti_analyze, type(result.user_mbti_analyze))
    print(result.mbti_type, type(result.mbti_type))
    print(result.psychological_analysis_type, type(result.psychological_analysis_type))
    print(result.psychological_analysis, type(result.psychological_analysis))
    print(result.created_at, type(result.created_at))
    print(result.create_time, type(result.create_time))
    print(result.update_time, type(result.update_time))


if __name__ == '__main__':
    asyncio.run(main())

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserModel(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(String(50))
    twitter_id = Column(String(50))
    twitter_username = Column(String(50))
    user_tweets = Column(Text)
    user_mbti_analyze = Column(Text)
    mbti_type = Column(String(32))
    psychological_analysis_type = Column(String(32))
    psychological_analysis = Column(Text)
    twitter_verified = Column(String(2))
    created_at = Column(DateTime)
    create_time = Column(String(16))
    update_time = Column(String(16))

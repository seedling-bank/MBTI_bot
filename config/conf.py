from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_BASE: str = "https://api.openai-sb.com/v1/"
    API_KEY: str = "sb-4dddef154335adacb0a1afbd2898053710ddecd9b47ba009"

    proxies: dict = {
        'http': 'http://205.198.65.182:38080',
        'https': 'http://205.198.65.182:38080'
    }
    TWITTER_BEARER_TOKEN: str = ("AAAAAAAAAAAAAAAAAAAAADOVuAEAAAAAepvUyZcEuzhGYwA3E9j2sXBgidA"
                                 "%3D0bK3m8IO6qQMb0vdqo0QAKFOGqIWzlpgYKTHlv6fLXhwXZXY5y")
    TWITTER_API_KEY: str = "xI3gtThwFLRiGTi6LNEN7wOo6"
    TWITTER_API_SECRET: str = "6HtZ3Dcs7gfLLOfjD0uneoX63z2r8jjZRQrJyFUX04EkY3DgW8"

    APIDANCE_API_KEY: str = "veyizsgc0f5x4mbl5k4xmajxvkhjex"

    MAX_RETRIES: int = 5
    DELAY: int = 5

    # 测试环境
    # DATABASE_URI: str = "mysql+aiomysql://root:mm123123@127.0.0.1:3306/mbti"
    # 正式环境
    DATABASE_URI: str = "mysql+aiomysql://cb:cryptoBricks123@cb-rds.cw5tnk9dgstt.us-west-2.rds.amazonaws.com:3306/mbti"


settings = Settings()

import asyncio
import traceback
import urllib.parse

import loguru


async def generate_twitter_link(twitter_name, custom_phrase, custom_address):
    try:
        # 定义模板文本，其中包含占位符
        template_text = """
        🌌 Application #10233 - MBTI PUMP 🚀
        🔍 {twitter_name} belongs to the {custom_phrase} camp  
         📍 Address: {custom_address}
        Join🪐✨ #MBTIPUMP 
        """

        # 使用自定义文本替换占位符
        customized_text = template_text.format(twitter_name=twitter_name,
                                               custom_phrase=custom_phrase, custom_address=custom_address)

        # 对文本进行URL编码
        encoded_text = urllib.parse.quote(customized_text)

        # 生成Twitter发帖链接
        twitter_link = f"https://twitter.com/intent/tweet?text={encoded_text}"

        return twitter_link

    except Exception as e:
        loguru.logger.error(e)
        loguru.logger.error(traceback.format_exc())


async def main():
    result = await generate_twitter_link("miaomiao", "B", "asdadadad")
    print(result)

if __name__ == '__main__':
    asyncio.run(main())

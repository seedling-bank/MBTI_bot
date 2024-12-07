import urllib.parse

# 文本内容
text = """🌌 Application #10233 - MBTI PUMP 🚀
🔍 miaomiao belongs to the B camp  
📍 Address: asdadadad
Join🪐✨ #MBTIPUMP"""

# URL 编码
encoded_text = urllib.parse.quote(text)

# 拼接到 Twitter 链接
twitter_url = f"https://twitter.com/intent/tweet?text={encoded_text}"

print(twitter_url)

import re


def extract_mbti(text):
    # 定义正则表达式模式来匹配MBTI结果
    pattern = r"用户的MBTI是：<b>(.*?)</b>"

    # 使用正则表达式搜索文本
    match = re.search(pattern, text)

    # 如果找到匹配，返回MBTI结果
    if match:
        return match.group(1)
    else:
        return None


template_text = """
"<b>🌟 用户的MBTI分析报告 🌟</b>

🧠 用户的MBTI是：<b>ENTP</b>

📊 分析如下：
<b>🔵 内向与外向（I/E）：</b> <b>E</b> 用户积极参与多个web3项目（MBTI PUMP, DA），并转发推广，显示出外向的社交倾向和寻求外部刺激的意愿。 推文中多次使用“Join”，“Claim”等号召性词汇，也表明其乐于与人互动，积极参与社区活动。

<b>🟢 实感与直觉（S/N）：</b> <b>N</b> 用户关注AI反馈协议（DA），以及AlphaX等新兴项目，显示出对新技术和未来趋势的关注，而非专注于已有的、可感知的事物。 推文内容多为项目推广和未来收益的展望，体现了直觉型思维的特征。

<b>🔴 思考与情感（T/F）：</b> <b>T</b> 用户的推文内容大多是客观地介绍项目，并着重强调项目特点及收益，例如“Proof-of-Insight”、“$1M incentiv…”等，较少表达个人情感，显示出理性且以逻辑为导向的思考模式。

<b>🟡 判断与感知（J/P）：</b> <b>P</b> 用户同时参与多个项目，且推文内容显示其对新项目和机会保持开放和灵活的态度。 这符合感知型的特点，而非注重计划和结构的判断型。


<b>🎉 和用户有同样MBTI的名人 🎉</b>
✨ 埃隆·马斯克，以其创新思维和对未来科技的远见卓识而闻名。"
"""

mbti_result = extract_mbti(template_text)
print(f"The extracted MBTI result is: {mbti_result}")

import traceback

import google.generativeai as genai
import loguru


async def mbti_genai_analysis(data, name):
    try:
        genai.configure(api_key="AIzaSyAk7VmYzRN1IG9GiRf3luB1jHrgzkcOUac")
        model = genai.GenerativeModel("gemini-1.5-flash")
        test = f"""
        text: '# 用户推文

        {data}

        # 执行步骤

        从用户推文中获取近期推文，并且结合简介内容推断用户可能的喜好/职业/习惯

        推断用户的MBTI，判断标准如下：

        I/E:

        I: Introverted individuals prefer solitary activities and get exhausted
        by social interaction. They tend to be quite sensitive to external stimulation
        (e.g. sound, sight or smell) in general. / E: Extraverted individuals
        prefer group activities and get energized by social interaction. They
        tend to be more enthusiastic and more easily excited than Introverts.

        S/N:

        S: Observant individuals are highly practical, pragmatic and down-to-earth.
        They tend to have strong habits and focus on what is happening or has
        already happened. / N: Intuitive individuals are very imaginative, open-minded
        and curious. They prefer novelty over stability and focus on hidden meanings
        and future possibilities.

        T/F:

        T: Thinking individuals focus on objectivity and rationality, prioritizing
        logic over emotions. They tend to hide their feelings and see efficiency
        as more important than cooperation. / F: Feeling individuals are sensitive
        and emotionally expressive. They are more empathic and less competitive
        than Thinking types, and focus on social harmony and cooperation.

        J/P:

        J: Judging individuals are decisive, thorough and highly organized. They
        value clarity, predictability and closure, preferring structure and planning
        to spontaneity. / P: Prospecting individuals are very good at improvising
        and spotting opportunities. They tend to be flexible, relaxed nonconformists
        who prefer keeping their options open.

        请记住分析的结果，要输出的分析报告中要使用这个结果

        # 格式

        以下示例内容中“//”表示注释符号，其内容不能出现在输出的内容中

        以下示例内容假设用户的MBTI为XXXX，在实际输出过程中需要改为上面分析的MBTI，样例输出如下：

        <b>🌟 {name}的MBTI分析报告 🌟</b>

        🧠 {name}的MBTI是：<b>XXXX</b>

        📊 分析如下：
        <b>🔵 内向与外向（I/E）：</b> // 开头写I/E的结论，后面内容结合具体推文或简介的内容进行分析
        <b>🟢 实感与直觉（S/N）：</b> // 开头写S/N的结论，后面内容结合具体推文或简介的内容进行分析
        <b>🔴 思考与情感（T/F）：</b> // 开头写T/F的结论，后面内容结合具体推文或简介的内容进行分析
        <b>🟡 判断与感知（J/P）：</b> // 开头写J/P的结论，后面内容结合具体推文或简介的内容进行分析
        
        <b>🎉 和{name}有同样MBTI的名人 🎉</b>
        ✨ // 介绍一个相同MBTI的名人，写一句话的内容。

        """
        response = model.generate_content(test)
        return response.text
    except Exception as e:
        loguru.logger.error(e)
        loguru.logger.error(traceback.format_exc())


"""
**{name}的MBTI分析报告**

        {name}的MBTI是：**XXXX**

        分析如下：

        - **内向与外向（I/E）**：// 开头写I/E的结论，后面内容结合具体推文或简介的内容进行分析

        - **实感与直觉（S/N）**：// 开头写S/N的结论，后面内容结合具体推文或简介的内容进行分析

        - **思考与情感（T/F）**：// 开头写T/F的结论，后面内容结合具体推文或简介的内容进行分析

        - **判断与感知（J/P）**：// 开头写J/P的结论，后面内容结合具体推文或简介的内容进行分析

        ---

        **和{name}有同样MBTI的名人**

        //介绍一个相同MBTI的名人，写一句话的内容。'
"""
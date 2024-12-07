import json

mbti_to_custom = {
    'ESTP': 'SARB',
    'ESFP': 'SAEB',
    'ISTP': 'SCRP',
    'ISFP': 'SCEB',
    'ESTJ': 'SCRB',
    'ESFJ': 'LCRP',
    'ISTJ': 'LCRB',
    'ISFJ': 'LCEB',
    'ENTJ': 'LARB',
    'ENTP': 'LARP',
    'INTJ': 'SAEP',
    'INTP': 'SARP',
    'ENFJ': 'LAEP',
    'ENFP': 'LAEB',
    'INFJ': 'LCEP',
    'INFP': 'SCEP',
}


def match_mbti_to_custom(mbti_type):
    print(mbti_type)
    return mbti_to_custom.get(mbti_type)


def get_mbti_analysis(psychological_analysis_type):
    with open("config/result.json", "r", encoding="utf-8") as file:
        result_data = json.load(file)
    print(psychological_analysis_type)
    data = result_data.get(psychological_analysis_type)
    print(data, type(data))
    return data

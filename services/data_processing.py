import traceback

import loguru


async def user_data_processing(user_data):
    try:
        if user_data:
            data = user_data.get('data', None)
            if data:
                user = data.get('user', None)
                if user:
                    result = user.get('result', None)
                    if result:
                        timeline_v2 = result.get('timeline_v2', None)
                        if timeline_v2:
                            timeline = timeline_v2.get('timeline', None)
                            if timeline:
                                instructions = timeline.get('instructions', None)
                                if instructions:
                                    for index_instruction, instruction in enumerate(instructions):
                                        if instruction.get('type') == "TimelineAddEntries":
                                            entries = instruction.get('entries', None)
                                            if entries:
                                                text_list = ""
                                                for index_entrie, entrie in enumerate(entries):
                                                    if index_entrie >= 5:
                                                        break
                                                    content = entrie.get('content', None)
                                                    if content:
                                                        itemContent = content.get('itemContent', None)
                                                        if itemContent:
                                                            tweet_results = itemContent.get('tweet_results', None)
                                                            if tweet_results:
                                                                result = tweet_results.get('result', None)
                                                                if result:
                                                                    tweet = result.get('tweet', None)
                                                                    if tweet:
                                                                        legacy = tweet.get('legacy', None)
                                                                    else:
                                                                        legacy = result.get('legacy', None)
                                                                        if legacy:
                                                                            full_text = legacy.get('full_text', None)
                                                                            text_list += (str(
                                                                                index_entrie + 1)
                                                                                          + '.' + full_text + '\n')
                                                                        else:
                                                                            return None
                                                                else:
                                                                    return None
                                                            else:
                                                                return None
                                                        else:
                                                            return None
                                                    else:
                                                        return None
                                                return text_list
        else:
            return None
    except Exception as e:
        loguru.logger.error(e)
        loguru.logger.error(traceback.format_exc())

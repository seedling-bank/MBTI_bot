import asyncio
import traceback

import loguru
import tweepy
import httpx
import requests
import json

import config.conf


async def get_user_twitter_id_by_tweepy(username: str):
    """
    通过tweepy获取twitter id
    :param username:
    :return:
    """
    try:
        client = tweepy.Client(bearer_token=config.conf.settings.TWITTER_BEARER_TOKEN)
        user_info = client.get_user(username=username)

        print(user_info.data)
        print(user_info.data.id)
    except Exception as e:
        loguru.logger.error(e)
        loguru.logger.error(traceback.format_exc())


async def get_user_twitter_id_by_api(username: str):
    """
    直接获取twitter id
    :param username:
    :return:
    """
    try:
        # 1. 请求的 URL
        url = "https://x.com/i/api/graphql/-0XdHI-mrHWBQd8-oLo1aA/ProfileSpotlightsQuery"

        # 2. 请求的变量
        variables = {
            "screen_name": f"{username}"  # 替换为你需要查询的用户名
        }
        auth_token = "e924a598897db19027037310e1df54b35e938611"
        # 3. 请求头
        headers = await get_twitter_headers(auth_token=auth_token)
        # 4. 发送请求
        response = requests.get(url, headers=headers, params={"variables": json.dumps(variables)})

        # 5. 处理响应
        if response.status_code == 200:
            data = response.json()
            if data:
                user_id = data.get('data').get('user_result_by_screen_name').get('result').get('rest_id')
                return user_id
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        loguru.logger.error(e)
        loguru.logger.error(traceback.format_exc())


async def get_user_twitter_id_by_apidance(username: str):
    """
    通过apidance获取twitter id
    :param username:
    :return:
    """
    try:
        url = f"https://api.apidance.pro/1.1/users/show.json?screen_name={username}"
        payload = {}
        headers = {
            'apikey': config.conf.settings.APIDANCE_API_KEY
        }
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        user_info = dict()
        if data:
            user_info['user_id'] = data.get('id')
            user_info['user_name'] = data.get('screen_name')

        return user_info
    except Exception as e:
        loguru.logger.error(e)
        loguru.logger.error(traceback.format_exc())


async def get_twitter_headers(auth_token):
    try:
        url = "https://twitter.com/i/api/graphql/nK1dw4oV3k4w5TdtcAdSww/SearchTimeline"

        headers = {
            "authority": "twitter.com",
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs"
                             "%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
            "cache-control": "no-cache",
            "cookie": f"auth_token={auth_token};ct0=",
            "pragma": "no-cache",
            "referer": "https://twitter.com/",
            "sec-ch-ua": '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/113.0.0.0 Safari/537.36",
            "x-csrf-token": "",  # ct0
            "x-twitter-active-user": "yes",
            "x-twitter-auth-type": "OAuth2Session",
            "x-twitter-client-language": "zh-cn",
        }

        client = httpx.Client(headers=headers)

        res1 = client.get(url)
        print(f"{res1.status_code} {res1.text}")
        # 第一次访问用于获取response cookie中的ct0字段，并添加到x-csrf-token与cookie中
        ct0 = res1.cookies.get("ct0")

        client.headers.update(
            {"x-csrf-token": ct0, "cookie": f"auth_token={auth_token};ct0={ct0}"}
        )

        return client.headers

    except Exception as e:
        loguru.logger.error(e)
        loguru.logger.error(traceback.format_exc())


async def get_user_twitter_data(name: str, user_id: int):
    try:
        if user_id:
            headers = {
                "accept": "*/*",
                "accept-language": "en,zh-CN;q=0.9,zh;q=0.8",
                "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81"
                                 "IUq16cHjhLTvJu4FA33AGWWjCpTnA",
                "content-type": "application/json",
                "priority": "u=1, i",
                "referer": f"https://x.com/{name}",
                "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"macOS\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
                              " Chrome/131.0.0.0 Safari/537.36",
                "x-client-transaction-id": "Qo0w/h0U99f8qSvZ+zwyrMVwk3ETDJfbddEyMa/Ux35Faw3qklJFr/bwxEqmaZqm5MxRvEB"
                                           "k30eUc+V8ngowkHMfHIvVQQ",
                "x-client-uuid": "18ce18cc-8855-430f-8625-c13e20476e14",
                "x-csrf-token": "03c28837150b045c7822e4341255935df26afad576b1bd30838036e98ccc051ce93f53a2cd9f0ab86a63"
                                "a69e741fc98d7be9901e6e3e3f8b12fd16285c551191792366ab428f80147cf3ba33ed253641",
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "x-twitter-client-language": "zh-cn"
            }
            cookies = {
                "night_mode": "2",
                "kdt": "6Jsjdw9jBcUpUbcg42CKP7h91QOXNDvxYLF2G9cD",
                "g_state": "{\"i_l\":0}",
                "d_prefs": "MToxLGNvbnNlbnRfdmVyc2lvbjoyLHRleHRfdmVyc2lvbjoxMDAw",
                "des_opt_in": "Y",
                "_ga": "GA1.2.189105086.1722318266",
                "twtr_pixel_opt_in": "Y",
                "_monitor_extras": "{\"deviceId\":\"8yCmrHcyVRXoBMdSG6CZmI\",\"eventId\":2,\"sequenceNumber\":2}",
                "first_ref": "https%3A%2F%2Fwww.google.com.hk%2F",
                "ph_phc_bzX9JlZsQjvFToje6i6tSVWZfspK1AUi14i4CzvcNY6_posthog": "%7B%22distinct_id%22%3A%22019256c6-11b0-"
                                                                              "7764-bd02-b6eff1774932%22%2C%22%24sesid"
                                                                              "%22%3A%5B1732717078390%2C%2201936df6-5a"
                                                                              "b7-7f30-b709-7c31a1395d13%22%2C17327166"
                                                                              "81911%5D%7D",
                "personalization_id": "\"v1_SrwQkfMX45L0z6yoJKQOEw==\"",
                "lang": "zh-cn",
                "ads_prefs": "\"HBERAAA=\"",
                "auth_multi": "\"1661204064376348672:bf5b1f925ab1d735efb839258b4c92f415df9cf2\"",
                "auth_token": "d3811db7402ba47e8acdd25781a0c6b0831be613",
                "twid": "u%3D1709536223294017537",
                "guest_id": "v1%3A173311018921236943",
                "ct0": "03c28837150b045c7822e4341255935df26afad576b1bd30838036e98ccc051ce93f53a2cd9f0ab86a63a69e741fc"
                       "8d7be9901e6e3e3f8b12fd16285c551191792366ab428f80147cf3ba33ed253641",
                "guest_id_ads": "v1%3A173311018921236943",
                "guest_id_marketing": "v1%3A173311018921236943",
                "amp_56bf9d": "ec9aa7bc-c84d-4d4f-80c6-c392c8593be9...1ie35bgqc.1ie37hj04.e.2r.39"
            }
            url = "https://x.com/i/api/graphql/sr_gr-uFoZ9sKVYy0GHzaA/UserTweets"
            variables = {
                "userId": f"{user_id}",
                "count": 20,
                "includePromotedContent": True,
                "withQuickPromoteEligibilityTweetFields": True,
                "withVoice": True,
                "withV2Timeline": True,
            }

            features = {
                "profile_label_improvements_pcf_label_in_post_enabled": False,
                "rweb_tipjar_consumption_enabled": True,
                "responsive_web_graphql_exclude_directive_enabled": True,
                "verified_phone_label_enabled": False,
                "creator_subscriptions_tweet_preview_api_enabled": True,
                "responsive_web_graphql_timeline_navigation_enabled": True,
                "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
                "communities_web_enable_tweet_community_results_fetch": True,
                "c9s_tweet_anatomy_moderator_badge_enabled": True,
                "articles_preview_enabled": True,
                "responsive_web_edit_tweet_api_enabled": True,
                "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
                "view_counts_everywhere_api_enabled": True,
                "longform_notetweets_consumption_enabled": True,
                "responsive_web_twitter_article_tweet_consumption_enabled": True,
                "tweet_awards_web_tipping_enabled": False,
                "creator_subscriptions_quote_tweet_preview_enabled": False,
                "freedom_of_speech_not_reach_fetch_enabled": True,
                "standardized_nudges_misinfo": True,
                "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
                "rweb_video_timestamps_enabled": True,
                "longform_notetweets_rich_text_read_enabled": True,
                "longform_notetweets_inline_media_enabled": True,
                "responsive_web_enhance_cards_enabled": False,
                "tweetypie_unmention_optimization_enabled": True,
                "rweb_lists_timeline_redesign_enabled": True,
                "responsive_web_media_download_video_enabled": True
            }
            fieldToggles = {
                'withArticlePlainText': False
            }

            parameters = {
                "queryId": "uYU5M2i12UhDvDTzN6hZPg",
                "variables": json.dumps(variables),
                "features": json.dumps(features),
                "fieldToggles": json.dumps(fieldToggles)
            }

            with httpx.Client(headers=headers, cookies=cookies) as client:
                response = client.get(url=url, params=parameters, timeout=300000)

            return response.json()
        else:
            return None
    except Exception as e:
        loguru.logger.error(e)
        loguru.logger.error(traceback.format_exc())


async def get_user_twitter_data_by_apidance(user_id: str):
    try:
        if user_id:
            base_url = "https://api.apidance.pro/graphql/UserTweets?variables="
            payload = {}
            headers = {
                'apikey': config.conf.settings.APIDANCE_API_KEY
            }

            variables = {
                "userId": user_id,
                "count": 20,
                "includePromotedContent": False,
                "withQuickPromoteEligibilityTweetFields": True,
                "withVoice": True,
                "withV2Timeline": True,
            }
            url = base_url + json.dumps(variables)
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                data = response.json()
                return data
        else:
            return None
    except Exception as e:
        loguru.logger.error(e)
        loguru.logger.error(traceback.format_exc())


async def main():
    name = "DeAgentAI"
    # user_data = await get_user_twitter_id_by_apidance(name)
    user_data = await get_user_twitter_id_by_api(name)
    print(user_data)

    user_id = "1753744475464052736"
    user_data = await get_user_twitter_data_by_apidance(user_id)
    print(user_data)


if __name__ == '__main__':
    asyncio.run(main())

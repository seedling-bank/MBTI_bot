import json

import loguru
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters, CallbackQueryHandler, CallbackContext,
)
import resources.languages
from services.users_services import (create_user, update_user_twitter, update_user_mbti,
                                     update_user_psychological_state, update_user_twitter_claim)
from utils.address_verify import address_verification
from utils.generate_twitter_link import generate_twitter_link
from utils.get_mbti import extract_mbti
from utils.gpt_transactions import get_gpt_translation, get_gpt_china_translation, get_gpt_english_translation
from utils.mbti_mapping import match_mbti_to_custom, get_mbti_analysis
from utils.tweet_verification import get_tweet_verification
from utils.user_id_verification import verify_user_id
from utils.user_mbti_analyze import get_user_mbti_analyze
from utils.user_twitter_article import get_user_twitter_article
from utils.verify_user import verify_user

# 定义状态

CHOOSE_LANGUAGE, HANDLE_TWITTER_LINK, HANDLE_TWITTER_ID, CONFIRMATION = range(4)

user_data = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_language = update.effective_user.language_code or 'en'
    if user_language not in resources.languages.LANGUAGES:
        user_language = 'en'
    context.user_data['language'] = user_language

    # 发送欢迎消息和语言选择键盘
    keyboard = [[InlineKeyboardButton(key, callback_data=key) for key in resources.languages.LANGUAGE_OPTIONS.keys()]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        resources.languages.LANGUAGES[user_language]['welcome'] + '\n' +
        resources.languages.LANGUAGES[user_language]['choose_language'],
        reply_markup=reply_markup
    )

    # 返回状态，进入语言选择阶段
    return CHOOSE_LANGUAGE


async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 获取用户点击的回调数据
    query = update.callback_query
    await query.answer()  # 确认回调已收到

    user_choice = query.data  # 获取回调数据

    if user_choice in resources.languages.LANGUAGE_OPTIONS:
        # 更新用户语言
        selected_language = resources.languages.LANGUAGE_OPTIONS[user_choice]
        context.user_data['language'] = selected_language

        # 回复用户选择的语言
        success_message = resources.languages.LANGUAGES[selected_language]['language_set_success']
        await query.edit_message_text(success_message)

        # 发送额外的介绍信息
        introduction_message = resources.languages.LANGUAGES[selected_language]['introduction']
        await query.message.reply_text(introduction_message)

        # 发送下一步提示
        next_step_message = resources.languages.LANGUAGES[selected_language]['next_step']
        await query.message.reply_text(next_step_message)

        next_steps_message = resources.languages.LANGUAGES[selected_language]['next_steps']
        await query.message.reply_text(next_steps_message)

        # 返回状态，进入twitter name处理阶段
        return HANDLE_TWITTER_ID

    else:
        # 如果用户选择无效（理论上不会发生，因为按钮是固定的）
        user_language = context.user_data.get('language', 'en')  # 默认语言为英语
        invalid_message = resources.languages.LANGUAGES[user_language]['invalid_choice']
        await query.edit_message_text(invalid_message)

        # 返回选择语言状态
        return CHOOSE_LANGUAGE


async def handle_twitter_id(update: Update, context: CallbackContext):
    user_language = context.user_data.get('language', 'en')

    telegram_id = update.effective_user.id  # 获取 Telegram 用户 ID
    twitter_name = update.message.text  # 获取用户输入的 Twitter ID

    # 保存用户的 Twitter ID（可以存储到数据库或内存中）
    user_data[telegram_id] = twitter_name
    context.user_data['telegram_id'] = telegram_id

    # 回复用户确认消息
    reply_to_user_confirmation_mseeage = resources.languages.LANGUAGES[user_language]['reply_to_user_confirmation']
    await update.message.reply_text(reply_to_user_confirmation_mseeage.format(twitter_id=twitter_name))

    # 验证用户输入的twitter name是否时有效的
    user_info = await verify_user_id(twitter_name)
    context.user_data['twitter_name'] = user_info
    if user_info is None:
        user_error_message = resources.languages.LANGUAGES[user_language]['user_error_message']
        await update.message.reply_text(user_error_message)
        return
    else:
        user_success_message = resources.languages.LANGUAGES[user_language]['user_success_message']
        await update.message.reply_text(user_success_message)

        # 验证用户是否存在
        user_info_data = await verify_user(telegram_id=telegram_id, twitter_id=user_info)
        # 如果用户存在且已通过twitter验证
        if user_info_data and user_info_data.twitter_verified == "1":
            user_tweets = user_info_data.user_tweets
            user_mbti_analyze = user_info_data.user_mbti_analyze
            mbti_type = user_info_data.mbti_type
            psychological_analysis_type = user_info_data.psychological_analysis_type
            psychological_analysis = user_info_data.psychological_analysis

            if user_tweets:
                # 如果存在用户且存在user_tweets
                if user_mbti_analyze:
                    # 如果存在用户,存在user_tweets,且存在user_mbti_analyze，直接输出user_mbti_analyze
                    await update.message.reply_text(json.dumps(user_mbti_analyze))
                    if psychological_analysis:
                        # 如果存在用户,存在user_tweets,且存在user_mbti_analyze和psychological_analysis，
                        # 直接输出psychological_analysis
                        psychological_analysis = get_mbti_analysis(psychological_analysis_type)
                        # 输出分析
                        await update.message.reply_text(json.dumps(psychological_analysis))
                        # 输出图片
                        photo_path = f'photo/{psychological_analysis_type}.jpeg'
                        await update.message.reply_photo(photo_path)
                        return ConversationHandler.END
                    else:
                        psychological_analysis_type = match_mbti_to_custom(mbti_type)
                        psychological_analysis = get_mbti_analysis(psychological_analysis_type)

                        # 输出分析
                        await update.message.reply_text(json.dumps(psychological_analysis))
                        # 输出图片
                        photo_path = f'photo/{psychological_analysis_type}.jpeg'
                        await update.message.reply_photo(photo_path)
                        return ConversationHandler.END
                else:
                    user_mbti = await get_user_mbti_analyze(data=user_tweets, user_name=twitter_name)
                    if user_mbti is None:
                        mbti_analysis_error_message = resources.languages.LANGUAGES[user_language][
                            'mbti_analysis_error']
                        await update.message.reply_text(mbti_analysis_error_message)
                        return ConversationHandler.END
                    else:
                        if user_language == 'zh':
                            result = await get_gpt_china_translation(user_mbti)
                        elif user_language == 'vi':
                            result = await get_gpt_translation(user_mbti)
                        else:
                            result = await get_gpt_english_translation(user_mbti)

                        # 插入用户的mbti分析
                        mbti_type = extract_mbti(result)
                        await update_user_mbti(telegram_id=telegram_id, twitter_id=user_info,
                                               user_mbti_analyze=result, mbti_type=mbti_type)

                        await update.message.reply_text(result, parse_mode="HTML")

                        psychological_analysis_type = match_mbti_to_custom(mbti_type)
                        psychological_analysis = get_mbti_analysis(psychological_analysis_type)

                        await update_user_psychological_state(
                            telegram_id=telegram_id, twitter_id=user_info,
                            psychological_analysis_type=psychological_analysis_type,
                            psychological_analysis=psychological_analysis)

                        context.user_data['mbti_type'] = mbti_type
                        context.user_data['psychological_analysis'] = json.dumps(psychological_analysis)
                        context.user_data['psychological_analysis_type'] = psychological_analysis_type

                        address_input_message = resources.languages.LANGUAGES[user_language][
                            'address_input']
                        await update.message.reply_text(address_input_message)
                        return HANDLE_TWITTER_LINK
            else:
                user_twitter_data = await get_user_twitter_article(user_id=user_info)

                if user_twitter_data is None:
                    twitter_data_error_message = resources.languages.LANGUAGES[user_language]['twitter_data_error']
                    await update.message.reply_text(twitter_data_error_message)
                    return ConversationHandler.END
                else:
                    # 插入用户的twitter数据
                    user_tweet = await update_user_twitter(telegram_id=telegram_id, twitter_id=user_info,
                                                           user_tweets=user_twitter_data)
                    if user_tweet is None:
                        return ConversationHandler.END
                    else:
                        twitter_data_success_message = resources.languages.LANGUAGES[user_language][
                            'twitter_data_success']
                        await update.message.reply_text(twitter_data_success_message)

                        user_mbti = await get_user_mbti_analyze(data=user_twitter_data, user_name=twitter_name)
                        if user_mbti is None:
                            mbti_analysis_error_message = resources.languages.LANGUAGES[user_language][
                                'mbti_analysis_error']
                            await update.message.reply_text(mbti_analysis_error_message)
                            return ConversationHandler.END
                        else:
                            if user_language == 'zh':
                                result = await get_gpt_china_translation(user_mbti)
                            elif user_language == 'vi':
                                result = await get_gpt_translation(user_mbti)
                            else:
                                result = await get_gpt_english_translation(user_mbti)

                            # 插入用户的mbti分析
                            mbti_type = extract_mbti(result)

                            await update_user_mbti(telegram_id=telegram_id, twitter_id=user_info,
                                                   user_mbti_analyze=result, mbti_type=mbti_type)

                            await update.message.reply_text(result, parse_mode="HTML")

                            psychological_analysis_type = match_mbti_to_custom(mbti_type)
                            psychological_analysis = get_mbti_analysis(psychological_analysis_type)

                            await update_user_psychological_state(
                                telegram_id=telegram_id, twitter_id=user_info,
                                psychological_analysis_type=psychological_analysis_type,
                                psychological_analysis=psychological_analysis)

                            context.user_data['mbti_type'] = mbti_type
                            context.user_data['psychological_analysis'] = psychological_analysis
                            context.user_data['psychological_analysis_type'] = psychological_analysis_type

                            address_input_message = resources.languages.LANGUAGES[user_language][
                                'address_input']
                            await update.message.reply_text(address_input_message)
                            return HANDLE_TWITTER_LINK

        # 如果用户存在但未通过twitter验证
        elif user_info_data and user_info_data.twitter_verified == '0':
            user_tweets = user_info_data.user_tweets
            user_mbti_analyze = user_info_data.user_mbti_analyze
            mbti_type = user_info_data.mbti_type
            psychological_analysis_type = user_info_data.psychological_analysis_type
            psychological_analysis = user_info_data.psychological_analysis

            if user_tweets:
                # 如果存在用户且存在user_tweets,直接输出user_tweets
                await update.message.reply_text(user_tweets)
                if user_mbti_analyze:
                    # 如果存在用户,存在user_tweets,且存在user_mbti_analyze，直接输出user_mbti_analyze
                    await update.message.reply_text(user_mbti_analyze)
                    if psychological_analysis:
                        # 如果存在用户,存在user_tweets,且存在user_mbti_analyze和psychological_analysis，
                        # 直接输出psychological_analysis
                        psychological_analysis = get_mbti_analysis(psychological_analysis_type)

                        context.user_data['mbti_type'] = mbti_type
                        context.user_data['psychological_analysis'] = json.dumps(psychological_analysis)
                        context.user_data['psychological_analysis_type'] = psychological_analysis_type

                        address_input_message = resources.languages.LANGUAGES[user_language][
                            'address_input']
                        await update.message.reply_text(address_input_message)
                        return HANDLE_TWITTER_LINK

                    else:
                        psychological_analysis_type = match_mbti_to_custom(mbti_type)
                        psychological_analysis = get_mbti_analysis(psychological_analysis_type)

                        await update_user_psychological_state(
                            telegram_id=telegram_id, twitter_id=user_info,
                            psychological_analysis_type=psychological_analysis_type,
                            psychological_analysis=psychological_analysis)

                        context.user_data['mbti_type'] = mbti_type
                        context.user_data['psychological_analysis'] = json.dumps(psychological_analysis)
                        context.user_data['psychological_analysis_type'] = psychological_analysis_type

                        address_input_message = resources.languages.LANGUAGES[user_language][
                            'address_input']
                        await update.message.reply_text(address_input_message)
                        return HANDLE_TWITTER_LINK
                else:
                    user_mbti = await get_user_mbti_analyze(data=user_tweets, user_name=twitter_name)
                    if user_mbti is None:
                        mbti_analysis_error_message = resources.languages.LANGUAGES[user_language][
                            'mbti_analysis_error']
                        await update.message.reply_text(mbti_analysis_error_message)
                        return ConversationHandler.END
                    else:
                        if user_language == 'zh':
                            result = await get_gpt_china_translation(user_mbti)
                        elif user_language == 'vi':
                            result = await get_gpt_translation(user_mbti)
                        else:
                            result = await get_gpt_english_translation(user_mbti)

                        # 插入用户的mbti分析
                        mbti_type = extract_mbti(result)
                        await update_user_mbti(telegram_id=telegram_id, twitter_id=user_info,
                                               user_mbti_analyze=result, mbti_type=mbti_type)

                        await update.message.reply_text(result, parse_mode="HTML")

                        psychological_analysis_type = match_mbti_to_custom(mbti_type)
                        psychological_analysis = get_mbti_analysis(psychological_analysis_type)

                        await update_user_psychological_state(
                            telegram_id=telegram_id, twitter_id=user_info,
                            psychological_analysis_type=psychological_analysis_type,
                            psychological_analysis=psychological_analysis)

                        context.user_data['mbti_type'] = mbti_type
                        context.user_data['psychological_analysis'] = json.dumps(psychological_analysis)
                        context.user_data['psychological_analysis_type'] = psychological_analysis_type

                        address_input_message = resources.languages.LANGUAGES[user_language][
                            'address_input']
                        await update.message.reply_text(address_input_message)
                        return HANDLE_TWITTER_LINK

            else:
                user_twitter_data = await get_user_twitter_article(user_id=user_info)
                loguru.logger.error(f"user_twitter_data----------------{user_twitter_data}")

                if user_twitter_data is None:
                    twitter_data_error_message = resources.languages.LANGUAGES[user_language]['twitter_data_error']
                    await update.message.reply_text(twitter_data_error_message)
                    return
                else:
                    # 插入用户的twitter数据
                    user_tweet = await update_user_twitter(telegram_id=telegram_id, twitter_id=user_info,
                                                           user_tweets=user_twitter_data)
                    if user_tweet is None:
                        return
                    else:

                        twitter_data_success_message = resources.languages.LANGUAGES[user_language][
                            'twitter_data_success']
                        await update.message.reply_text(twitter_data_success_message)

                        user_mbti = await get_user_mbti_analyze(data=user_twitter_data, user_name=twitter_name)
                        if user_mbti is None:
                            mbti_analysis_error_message = resources.languages.LANGUAGES[user_language][
                                'mbti_analysis_error']
                            await update.message.reply_text(mbti_analysis_error_message)
                            return
                        else:
                            if user_language == 'zh':
                                result = await get_gpt_china_translation(user_mbti)
                            elif user_language == 'vi':
                                result = await get_gpt_translation(user_mbti)
                            else:
                                result = await get_gpt_english_translation(user_mbti)

                            # 插入用户的mbti分析
                            mbti_type = extract_mbti(result)
                            await update_user_mbti(telegram_id=telegram_id, twitter_id=user_info,
                                                   user_mbti_analyze=result, mbti_type=mbti_type)

                            await update.message.reply_text(result, parse_mode="HTML")

                            psychological_analysis_type = match_mbti_to_custom(mbti_type)
                            psychological_analysis = get_mbti_analysis(psychological_analysis_type)

                            await update_user_psychological_state(
                                telegram_id=telegram_id, twitter_id=user_info,
                                psychological_analysis_type=psychological_analysis_type,
                                psychological_analysis=psychological_analysis)

                            context.user_data['mbti_type'] = mbti_type
                            context.user_data['psychological_analysis'] = json.dumps(psychological_analysis)
                            context.user_data['psychological_analysis_type'] = psychological_analysis_type

                            address_input_message = resources.languages.LANGUAGES[user_language][
                                'address_input']
                            await update.message.reply_text(address_input_message)
                            return HANDLE_TWITTER_LINK

        # 用户不存在
        else:
            # 如果没有用户则创建用户
            user_id = await create_user(telegram_id=telegram_id, twitter_id=user_info, twitter_username=twitter_name)

            if user_id is None:
                await update.message.reply_text(f"创建用户失败！")
                return
            else:
                # 继续下一步逻辑（获取twitter数据）
                twitter_data_processing_message = resources.languages.LANGUAGES[user_language][
                    'twitter_data_processing']
                await update.message.reply_text(twitter_data_processing_message)

                user_twitter_data = await get_user_twitter_article(user_id=user_info)
                loguru.logger.error(f"user_twitter_data----------------{user_twitter_data}")

                if user_twitter_data is None:
                    twitter_data_error_message = resources.languages.LANGUAGES[user_language]['twitter_data_error']
                    await update.message.reply_text(twitter_data_error_message)
                    return
                else:
                    # 插入用户的twitter数据
                    user_tweet = await update_user_twitter(telegram_id=telegram_id, twitter_id=user_info,
                                                           user_tweets=user_twitter_data)
                    if user_tweet is None:
                        return
                    else:

                        twitter_data_success_message = resources.languages.LANGUAGES[user_language][
                            'twitter_data_success']
                        await update.message.reply_text(twitter_data_success_message)

                        user_mbti = await get_user_mbti_analyze(data=user_twitter_data, user_name=twitter_name)
                        if user_mbti is None:
                            mbti_analysis_error_message = resources.languages.LANGUAGES[user_language][
                                'mbti_analysis_error']
                            await update.message.reply_text(mbti_analysis_error_message)
                            return
                        else:
                            if user_language == 'zh':
                                result = await get_gpt_china_translation(user_mbti)
                            elif user_language == 'vi':
                                result = await get_gpt_translation(user_mbti)
                            else:
                                result = await get_gpt_english_translation(user_mbti)

                            # 插入用户的mbti分析
                            mbti_type = extract_mbti(user_mbti)
                            await update_user_mbti(telegram_id=telegram_id, twitter_id=user_info,
                                                   user_mbti_analyze=result, mbti_type=mbti_type)

                            await update.message.reply_text(result, parse_mode="HTML")

                            psychological_analysis_type = match_mbti_to_custom(mbti_type)
                            psychological_analysis = get_mbti_analysis(psychological_analysis_type)
                            await update_user_psychological_state(
                                telegram_id=telegram_id, twitter_id=user_info,
                                psychological_analysis_type=psychological_analysis_type,
                                psychological_analysis=psychological_analysis)

                            context.user_data['mbti_type'] = mbti_type
                            context.user_data['psychological_analysis'] = json.dumps(psychological_analysis)
                            context.user_data['psychological_analysis_type'] = psychological_analysis_type

                            address_input_message = resources.languages.LANGUAGES[user_language][
                                'address_input']
                            await update.message.reply_text(address_input_message)
                            return HANDLE_TWITTER_LINK


async def handle_twitter_link(update: Update, context: CallbackContext):
    user_language = context.user_data.get('language', 'en')
    mbti_type = context.user_data.get('mbti_type')
    twitter_id = context.user_data.get('twitter_name')

    address = update.message.text

    # 判断address是否正确
    add_verify = await address_verification(address)

    if add_verify:
        address_verify_success_mseeage = resources.languages.LANGUAGES[user_language]['address_verify_success']
        await update.message.reply_text(address_verify_success_mseeage.format(address=address))

        # 提示生成twitter链接
        generate_link_message = resources.languages.LANGUAGES[user_language][
            'generate_link']
        await update.message.reply_text(generate_link_message)

        twitter_url = await generate_twitter_link(twitter_name=twitter_id,
                                                  custom_phrase=mbti_type, custom_address=address)

        # 给文字添加twitter 链接，提醒用户进行发文
        article_link_message = resources.languages.LANGUAGES[user_language][
            'article_link']
        await update.message.reply_text(
            f"<a href='{twitter_url}'>{article_link_message}</a>",
            parse_mode="HTML"
        )

        send_tweet_alerts_message = resources.languages.LANGUAGES[user_language][
            'send_tweet_alerts']
        await update.message.reply_text(send_tweet_alerts_message)

        # 创建确认按钮
        confirm_button_message = resources.languages.LANGUAGES[user_language][
            'confirm_button']
        cancel_button_message = resources.languages.LANGUAGES[user_language][
            'cancel_button']
        keyboard = [
            [
                InlineKeyboardButton(confirm_button_message, callback_data='confirm'),
                InlineKeyboardButton(cancel_button_message, callback_data='cancel')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        twitter_link_verification_message = resources.languages.LANGUAGES[user_language]['address_verify_success']
        await update.message.reply_text(
            twitter_link_verification_message.format(address=address, twitter_url=twitter_url),
            reply_markup=reply_markup
        )

        return CONFIRMATION
    else:
        address_verify_error_mseeage = resources.languages.LANGUAGES[user_language]['address_verify_error']
        await update.message.reply_text(address_verify_error_mseeage.format(address=address))


async def confirm_callback(update: Update, context: CallbackContext) -> int:
    user_language = context.user_data.get('language', 'en')
    twitter_id = context.user_data.get('twitter_name')
    telegram_id = context.user_data.get('telegram_id')
    psychological_analysis = context.user_data.get('psychological_analysis')
    psychological_analysis_type = context.user_data.get('psychological_analysis_type')

    query = update.callback_query
    await query.answer()  # 通过这个方法来响应回调查询

    confirm_message = resources.languages.LANGUAGES[user_language][
        'confirm']
    await query.edit_message_text(text=confirm_message)

    result = await get_tweet_verification(twitter_id=twitter_id)
    if result:
        await update_user_twitter_claim(telegram_id=telegram_id, twitter_id=twitter_id)
        # 输出分析

        await query.message.reply_text(json.dumps(psychological_analysis))
        # 输出图片
        photo_path = f'photo/{psychological_analysis_type}.jpeg'
        await query.message.reply_photo(photo_path)

        return ConversationHandler.END
    else:
        return ConversationHandler.END


async def cancel_callback(update: Update, context: CallbackContext) -> int:
    user_language = context.user_data.get('language', 'en')

    query = update.callback_query
    await query.answer()
    cancel_message = resources.languages.LANGUAGES[user_language][
        'cancel']
    await query.edit_message_text(text=cancel_message)

    tweet_verification_canceled_mseeage = resources.languages.LANGUAGES[user_language][
        'tweet_verification_canceled']
    await update.message.reply_text(tweet_verification_canceled_mseeage)

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """取消对话"""
    await update.message.reply_text("Conversation canceled. You can start again with /start.")
    return ConversationHandler.END


def main():
    application = Application.builder().token("7641581334:AAHXEfIpnXRB_h5YHUpjBFFMnwVSy_I1uek").build()
    # 测试
    # application = Application.builder().token("7515684358:AAHrGENRadK0N54nbkwDGgDI6V4jgnvhUyA").build()

    # 定义对话处理器
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_LANGUAGE: [CallbackQueryHandler(choose_language)],
            HANDLE_TWITTER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_twitter_id)],
            HANDLE_TWITTER_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_twitter_link)],
            CONFIRMATION: [
                CallbackQueryHandler(confirm_callback, pattern='^confirm$'),
                CallbackQueryHandler(cancel_callback, pattern='^cancel$')
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()

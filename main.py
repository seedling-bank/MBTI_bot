import asyncio

import loguru
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters, CallbackQueryHandler, CallbackContext,
)
import config.conf
import resources.languages
from utils.gpt_transactions import get_gpt_translation, get_gpt_china_translation, get_gpt_english_translation
from utils.user_id_verification import verify_user_id
from utils.user_mbti_analyze import get_user_mbti_analyze
from utils.user_twitter_article import get_user_twitter_article

# 定义状态
CHOOSE_LANGUAGE = 1
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

        # 结束对话
        return ConversationHandler.END

    else:
        # 如果用户选择无效（理论上不会发生，因为按钮是固定的）
        user_language = context.user_data.get('language', 'en')  # 默认语言为英语
        invalid_message = resources.languages.LANGUAGES[user_language]['invalid_choice']
        await query.edit_message_text(invalid_message)

        # 返回选择语言状态
        return CHOOSE_LANGUAGE


async def handle_twitter_id(update: Update, context: CallbackContext):
    user_language = context.user_data.get('language', 'en')

    user_id = update.effective_user.id  # 获取 Telegram 用户 ID
    twitter_id = update.message.text  # 获取用户输入的 Twitter ID

    # 保存用户的 Twitter ID（可以存储到数据库或内存中）
    user_data[user_id] = twitter_id

    # 回复用户确认消息
    reply_to_user_confirmation_mseeage = resources.languages.LANGUAGES[user_language]['reply_to_user_confirmation']
    await update.message.reply_text(reply_to_user_confirmation_mseeage.format(twitter_id=twitter_id))

    user_info = await verify_user_id(twitter_id)

    if user_info is None:
        user_error_message = resources.languages.LANGUAGES[user_language]['user_error_message']
        await update.message.reply_text(user_error_message)
        return
    else:
        user_success_message = resources.languages.LANGUAGES[user_language]['user_success_message']
        await update.message.reply_text(user_success_message)

        # 继续下一步逻辑（获取twitter数据）
        twitter_data_processing_message = resources.languages.LANGUAGES[user_language]['twitter_data_processing']
        await update.message.reply_text(twitter_data_processing_message)

        await asyncio.sleep(config.conf.settings.DELAY)
        user_twitter_data = await get_user_twitter_article(user_id=user_info)
        # loguru.logger.error(f"user_twitter_data----------------{user_twitter_data}")
        if user_twitter_data is None:
            twitter_data_error_message = resources.languages.LANGUAGES[user_language]['twitter_data_error']
            await update.message.reply_text(twitter_data_error_message)
        else:
            twitter_data_success_message = resources.languages.LANGUAGES[user_language]['twitter_data_success']
            await update.message.reply_text(twitter_data_success_message)

            user_mbti = await get_user_mbti_analyze(data=user_twitter_data, user_name=twitter_id)
            # loguru.logger.error(f"user_mbti----------------{user_mbti}")
            if user_mbti is None:
                mbti_analysis_error_message = resources.languages.LANGUAGES[user_language]['mbti_analysis_error']
                await update.message.reply_text(mbti_analysis_error_message)
            else:
                if user_language == 'zh':
                    result = await get_gpt_china_translation(user_mbti)
                elif user_language == 'vi':
                    result = await get_gpt_translation(user_mbti)
                else:
                    result = await get_gpt_english_translation(user_mbti)
                print(result)
                await update.message.reply_text(result, parse_mode="HTML")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """取消对话"""
    await update.message.reply_text("Conversation canceled. You can start again with /start.")
    return ConversationHandler.END


def main():
    # application = Application.builder().token("7641581334:AAHXEfIpnXRB_h5YHUpjBFFMnwVSy_I1uek").build()
    # 测试
    application = Application.builder().token("7515684358:AAHrGENRadK0N54nbkwDGgDI6V4jgnvhUyA").build()

    # 定义对话处理器
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_LANGUAGE: [CallbackQueryHandler(choose_language)],
        },
        fallbacks=[],
    )
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_twitter_id))
    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == "__main__":
    main()

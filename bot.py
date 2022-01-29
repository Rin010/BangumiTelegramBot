#!/usr/bin/python
"""
https://bangumi.github.io/api/
"""

import logging
import telebot

from config import BOT_TOKEN
from utils.api import run_continuously
from plugins import start, help, week, info, doing_page, search
from plugins.callback import now_do, rating_call, letest_eps, search_details, collection, week_back, summary_call
from plugins.inline import sender, public, mybgm

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)  # Outputs debug messages to console.
logging.basicConfig(level=logging.INFO,
                    filename='run.log',
                    format='%(asctime)s - %(filename)s & %(funcName)s[line:%(lineno)d] - %(levelname)s: %(message)s')
# 请求TG Bot api
bot = telebot.TeleBot(BOT_TOKEN)


# 查询/绑定 Bangumi ./plugins/start
@bot.message_handler(commands=['start'])
def send_start(message):
    start.send(message, bot)


# 使用帮助 ./plugins/help
@bot.message_handler(commands=['help'])
def send_help(message):
    help.send(message, bot)


# 查询 Bangumi 用户在看book ./plugins/doing_page
@bot.message_handler(commands=['book'])
def send_book(message):
    doing_page.send(message, bot, 1)


# 查询 Bangumi 用户在看anime ./plugins/doing_page
@bot.message_handler(commands=['anime'])
def send_anime(message):
    doing_page.send(message, bot, 2)


# 查询 Bangumi 用户在玩 game ./plugins/doing_page
@bot.message_handler(commands=['game'])
def send_game(message):
    doing_page.send(message, bot, 4)


# 查询 Bangumi 用户在看 real ./plugins/doing_page
@bot.message_handler(commands=['real'])
def send_real(message):
    doing_page.send(message, bot, 6)


# 每日放送查询 ./plugins/week
@bot.message_handler(commands=['week'])
def send_week(message):
    week.send(message, bot)


# 搜索引导指令 ./plugins/search
@bot.message_handler(commands=['search'])
def send_search_details(message):
    search.send(message, bot)


# 根据subjectId 返回对应条目信息 ./plugins/info
@bot.message_handler(commands=['info'])
def send_subject_info(message):
    info.send(message, bot)


# 空按钮回调处理
@bot.callback_query_handler(func=lambda call: call.data == 'None')
def callback_none(call):
    bot.answer_callback_query(call.id)


# 在看详情 ./plugins/callback/now_do
@bot.callback_query_handler(func=lambda call: call.data.split('|')[0] == 'now_do')
def now_do_callback(call):
    now_do.callback(call, bot)


# 评分 ./plugins/callback/rating_call
@bot.callback_query_handler(func=lambda call: call.data.split('|')[0] == 'rating')
def rating_callback(call):
    rating_call.callback(call, bot)


# 已看最新 ./plugins/callback/letest_eps
@bot.callback_query_handler(func=lambda call: call.data.split('|')[0] == 'letest_eps')
def letest_eps_callback(call):
    letest_eps.callback(call, bot)


# 批量更新 ./plugins/callback/bulk_eps 搁置
# @bot.callback_query_handler(func=lambda call: call.data.split('|')[0] == 'bulk_eps')
# def bulk_eps_callback(call):
#     bulk_eps.callback(call, bot)


# 在看列表 翻页 ./plugins/callback/now_do
@bot.callback_query_handler(func=lambda call: call.data.split('|')[0] == 'do_page')
def do_page_callback(call):
    now_do.callback_page(call, bot)


# 搜索详情页 ./plugins/callback/search_details
@bot.callback_query_handler(func=lambda call: call.data.split('|')[0] == 'search_details')
def search_details_callback(call):
    search_details.callback(call, bot)


# 收藏 ./plugins/callback/collection
@bot.callback_query_handler(func=lambda call: call.data.split('|')[0] == 'collection')
def collection_callback(call):
    collection.callback(call, bot)


# week 返回 ./plugins/callback/week_back
@bot.callback_query_handler(func=lambda call: call.data.split('|')[0] == 'back_week')
def back_week_callback(call):
    week_back.callback(call, bot)


# 简介 ./plugins/callback/summary_call
@bot.callback_query_handler(func=lambda call: call.data.split('|')[0] == 'summary')
def back_summary_callback(call):
    summary_call.callback(call, bot)


@bot.chosen_inline_handler(func=lambda chosen_inline_result: True)
def test_chosen(chosen_inline_result):
    logger.info(chosen_inline_result)


# inline 方式私聊搜索或者在任何位置搜索前使用@ ./plugins/inline/sender
@bot.inline_handler(lambda query: query.query and (query.chat_type == 'sender' or str.startswith(query.query, '@')) and not str.startswith(query.query, 'mybgm'))
def sender_query_text(inline_query):
    sender.query_sender_text(inline_query, bot)


# inline 方式公共搜索 ./plugins/inline/public
@bot.inline_handler(lambda query: query.query and query.chat_type != 'sender' and not str.startswith(query.query, '@') and not str.startswith(query.query, 'mybgm'))
def public_query_text(inline_query):
    public.query_public_text(inline_query, bot)


# inline 方式查询个人统计 ./plugins/inline/mybgm
@bot.inline_handler(lambda query: query.query and 'mybgm' in query.query)
def mybgm_query_text(inline_query):
    mybgm.query_mybgm_text(inline_query, bot)


@bot.inline_handler(lambda query: not query.query)
def query_empty(inline_query):
    bot.answer_inline_query(
        inline_query.id, [], switch_pm_text="@BGM条目ID或关键字搜索或使用mybgm查询数据", switch_pm_parameter="None", cache_time=0)


def set_bot_command(bot):
    """设置Bot命令"""
    commands_list = [
        telebot.types.BotCommand("help", "使用帮助"),
        telebot.types.BotCommand("book", "Bangumi用户在读书籍"),
        telebot.types.BotCommand("anime", "Bangumi用户在看动画"),
        telebot.types.BotCommand("game", "Bangumi用户在玩动画"),
        telebot.types.BotCommand("real", "Bangumi用户在看剧集"),
        telebot.types.BotCommand("week", "空格加数字查询每日放送"),
        telebot.types.BotCommand("search", "搜索条目"),
        telebot.types.BotCommand("start", "绑定Bangumi账号"),
    ]
    try:
        return bot.set_my_commands(commands_list)
    except:
        pass


# 开始启动
if __name__ == '__main__':
    set_bot_command(bot)
    stop_run_continuously = run_continuously()
    bot.infinity_polling()

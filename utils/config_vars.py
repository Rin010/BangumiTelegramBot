import yaml
from redis import Redis
from telebot.async_telebot import AsyncTeleBot

from .api import BangumiAPI
from .sqlite_orm import SQLite

# 配置
with open('data/config.yaml', 'r') as f:
    config: dict = yaml.safe_load(f)

CALLBACK_URL = f"{config['API_SERVER']['WEBSITE_BASE']}:{config['API_SERVER']['POST']}/oauth_callback"

# 创建 TeleBot 实例
bot = AsyncTeleBot(config["BOT_TOKEN"], parse_mode='Markdown')
BOT_USERNAME = bot.get_me().username

# bgm.tv API
bgm = BangumiAPI(
    config["BGM"]["APP_ID"],
    config["BGM"]["APP_SECRET"],
    CALLBACK_URL)

# 数据库
sql = SQLite()

redis = Redis(
    host=config['REDIS']['HOST'],
    port=config['REDIS']['PORT'],
    db=config['REDIS']['REDIS_DATABASE'])
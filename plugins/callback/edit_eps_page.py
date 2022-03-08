"""已看最新"""
import telebot

from model.page_model import EditEpsPageRequest, BackRequest, DoEditEpisodeRequest
from utils.api import post_eps_status, get_subject_episode, get_episode_info
from utils.converts import number_to_episode_type


def generate_page(request: EditEpsPageRequest, stack_uuid: str) -> EditEpsPageRequest:
    episode_id = request.episode_id
    episode_info = request.episode_info
    if not episode_info:
        episode_info = get_episode_info(request.episode_id)
    if episode_info['ep'].is_integer():
        ep = str(int(episode_info['ep']))
    else:
        ep = str(episode_info['ep'])
    text = f"*{number_to_episode_type(episode_info['type'])}.{ep}*"
    if episode_info['name_cn']:
        text += f"* | {episode_info['name_cn']}*"
    if episode_info['name']:
        text += f"* / {episode_info['name']}*"
    if episode_info['duration']:
        text += f"\n*➤ 时长：*`{episode_info['duration']}`\n"
    if episode_info['airdate']:
        text += f"*➤ 首播日期：*`{episode_info['airdate']}`\n"
    if episode_info['desc']:
        text += f"*➤ 章节简介：*\n{episode_info['desc']}\n"
    text += f"💬 [讨论：{episode_info['comment']}](https://bgm.tv/ep/{episode_id})"
    markup = telebot.types.InlineKeyboardMarkup()
    request.possible_request['back'] = BackRequest(request.session)
    if request.session.bot_message.chat.type == 'private' and request.before_status is not None:
        button_list = []
        if request.before_status != 2:
            button_list.append(telebot.types.InlineKeyboardButton(text="看过", callback_data=f'{stack_uuid}|watched'))
            request.possible_request['watched'] = DoEditEpisodeRequest(request.session, request.episode_id, 'watched')

        button_list.append(telebot.types.InlineKeyboardButton(text="看到", callback_data=f'{stack_uuid}|watched_batch'))
        request.possible_request['watched_batch'] = DoEditEpisodeRequest(request.session, request.episode_id,
                                                                         'watched_batch')
        if request.before_status != 1:
            button_list.append(telebot.types.InlineKeyboardButton(text="想看", callback_data=f'{stack_uuid}|queue'))
            request.possible_request['queue'] = DoEditEpisodeRequest(request.session, request.episode_id, 'queue')
        if request.before_status != 3:
            button_list.append(telebot.types.InlineKeyboardButton(text="抛弃", callback_data=f'{stack_uuid}|drop'))
            request.possible_request['drop'] = DoEditEpisodeRequest(request.session, request.episode_id, 'drop')
        if request.before_status != 0:
            button_list.append(telebot.types.InlineKeyboardButton(text="撤销", callback_data=f'{stack_uuid}|remove'))
            request.possible_request['remove'] = DoEditEpisodeRequest(request.session, request.episode_id, 'remove')
        markup.add(*button_list, row_width=5)

    markup.add(telebot.types.InlineKeyboardButton(text="返回", callback_data=f'{stack_uuid}|back'))
    request.page_markup = markup
    request.page_text = text
    return request


def do(request: DoEditEpisodeRequest, tg_id: int) -> DoEditEpisodeRequest:
    if request.status != 'watched_batch':
        post_eps_status(tg_id, request.episode_id, request.status)
        request.callback_text = '已修改'
    else:  # 批量更新
        episode_info = get_episode_info(request.episode_id)  # 查询所有要更新的ep
        page = 0
        limit = 200
        update_eps = []
        while True:
            data = get_subject_episode(episode_info['subject_id'], limit=limit, offset=limit * page,
                                       type_=episode_info['type'])
            page += 1
            ok = False
            for ep in data['data']:
                update_eps.append(ep['id'])
                if ep['id'] == request.episode_id:
                    ok = True
                    break
            if ok or data['total'] < limit or len(data['data']) < limit:
                break
        post_eps_status(tg_id, request.episode_id, 'watched', update_eps)
        request.callback_text = f'已修改{len(update_eps)}个章节为看过'
    return request
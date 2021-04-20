from VkUser import *
from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

with open('txts/group_token.txt', encoding='utf-8') as f:
    group_token = f.readline()

vk = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk)


def write_msg(user_id, message, attachment=''):
    vk.method('messages.send',
              {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), 'attachment': attachment})


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text
            user = VkUser(event.user_id)
            if request == "привет":
                write_msg(event.user_id, f"Хай, {event.user_id}")
            elif request == "пока":
                write_msg(event.user_id, event.user_id, "Пока((")
            elif 'страна ' in request:
                write_msg(event.user_id, user.country(request))
            elif 'город ' in request:
                write_msg(event.user_id, user.city(request))
            elif 'семейное положение' in request:
                write_msg(event.user_id, user.relation(request))
            elif 'дата рождения ' in request:
                write_msg(event.user_id, user.bdate(request))
            elif request == "подбери мне пару":
                check = user.what_i_need()
                if check is None:
                    pairs = user.get_short_list()
                    for person in pairs:
                        attachments = ','.join(person['photos'])
                        write_msg(event.user_id, f'Ваша пара:\n {person["url"]}', attachments)
                else:
                    write_msg(event.user_id, check)

            else:
                write_msg(event.user_id, "Не поняла вашего ответа...")

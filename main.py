import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll

import utils
from models import User
from config import *

class MyLongPoll(VkBotLongPoll):
    def listen(self):
        while True:
            try:
                for event in self.check():
                    yield event
            except Exception as e:
                print(e)

class VkBot:
    def __init__(self):
        self.vk_session = vk_api.VkApi(token=token)
        self.longpoll = MyLongPoll(self.vk_session, 215773838)

    def run(self):
        for event in self.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                msg = event.object.message
                user_id = msg['from_id']
                user = utils.get_user_by_id(user_id)
                text = msg['text']
                fwd = self.vk_session.method('messages.getByConversationMessageId', {
                    'conversation_message_ids': msg['conversation_message_id'],
                    'peer_id': msg['peer_id']
                })['items'][0]

                if 'reply_message' in fwd:
                    fwd = fwd['reply_message']
                else:
                    fwd = None

                if user.vk_id == admin_id:
                    if text == '!кик':
                        self.vk_session.method('messages.removeChatUser', {
                            'user_id': fwd['from_id'], #event.user_id,
                            'chat_id': msg['peer_id'] - 2000000000
                        })
                    elif text == '!пред' or text == '! пред':
                        fwd_user = utils.get_user_by_id(fwd['from_id'])
                        fwd_user.warns += 1
                        fwd_user.save()

                        user_name = self.vk_session.method('users.get', {
                            'user_id': fwd_user.vk_id
                        })[0]['first_name']
                        print(user_name)

                        self.vk_session.method('messages.send', {
                            'chat_id': msg['peer_id'] - 2000000000,
                            'message': f'{user_name}, вам выдано предупреждение! '
                                       f'\n Всего предупреждений: {fwd_user.warns} / 5',
                            'random_id': 0
                        })

                        if fwd_user.warns >= 5:
                            self.vk_session.method('messages.removeChatUser', {
                                'user_id': fwd_user.vk_id,
                                'chat_id': msg['peer_id'] - 2000000000
                            })

                    elif text == '!списокпредовочистить' or text == '! списокпредовочистить':
                        fwd_user = utils.get_user_by_id(fwd['from_id'])
                        fwd_user.warns = 0
                        fwd_user.save()

                        user_name = self.vk_session.method('users.get', {
                            'user_id': fwd_user.vk_id
                        })[0]['first_name']
                        print(user_name)

                        self.vk_session.method('messages.send', {
                            'chat_id': msg['peer_id'] - 2000000000,
                            'message': f'{user_name}, все предупреждения сняты! '
                                       f'\n Всего предупреждений: {fwd_user.warns} / 5',
                            'random_id': 0
                        })

                    elif text == '!распред' or text == '! распред':
                        fwd_user = utils.get_user_by_id(fwd['from_id'])
                        fwd_user.warns -= 1
                        fwd_user.save()

                        user_name = self.vk_session.method('users.get', {
                            'user_id': fwd_user.vk_id
                        })[0]['first_name']
                        print(user_name)

                        self.vk_session.method('messages.send', {
                            'chat_id': msg['peer_id'] - 2000000000,
                            'message': f'{user_name}, предупреждение снято! '
                                       f'\n Всего предупреждений: {fwd_user.warns} / 5',
                            'random_id': 0
                        })

                print(user_id, text, fwd)

if __name__ == '__main__':
    VkBot().run()
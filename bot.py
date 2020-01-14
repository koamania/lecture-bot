import json
import logging
from time import sleep

import websocket
from slacker import Slacker

import command


class Bot:

    def __init__(self, bot_token, api_token):
        self._botclient = Slacker(bot_token)
        self._apiclient = Slacker(api_token)

    def run(self):
        response = self._botclient.rtm.start()
        socket = websocket.create_connection(response.body['url'])
        socket.settimeout(60)
        while True:
            # noinspection PyBroadException
            try:
                received_event = json.loads(socket.recv())
                message_command = self._read(received_event)
                if message_command is None:
                    sleep(1)
                    continue
                else:
                    response_message = message_command.execute()
                    self._botclient.chat.post_message(channel=received_event['channel'], text=None,
                                                      attachments=response_message,
                                                      as_user=True)
            except websocket.WebSocketTimeoutException:
                socket.send(json.dumps({'type': 'ping'}))
            except Exception as ex:
                attachments_dict = dict()
                attachments_dict['pretext'] = '요청 처리 실패'
                attachments_dict['title'] = str(ex)
                attachments_dict['text'] = 'course help 명령어를 이용해서 사용법을 확인해주시길 바랍니다.' \
                                           '\n 그래도 오류나면 dhlee한테 말걸지 마세요'
                attachments_dict['mrkdwn_in'] = ['text', 'pretext']
                attachments_dict['color'] = '#ff0000'
                # logging.exception('execute command exception occurred')
                self._botclient.chat.post_message(channel=received_event['channel'], text=None,
                                                  attachments=[attachments_dict],
                                                  as_user=True)

    def _read(self, event):
        if event['type'] == 'message' and 'text' in event:
            return self._obtain_command(event)
        return None

    def _obtain_command(self, event):
        message = event['text']
        if message == 'course list':
            return command.List(message)
        elif message.startswith('course start'):
            user_profile = self._apiclient.users.profile.get(event['user'])
            profile = user_profile.body['profile']['display_name']
            return command.StartCourse(message, profile)
        elif message.startswith('course end'):
            return command.EndCourse(message)
        elif message.startswith('course add'):
            return command.AddCourse(message)
        elif message.startswith('course delete'):
            return command.DeleteCourse(message)
        elif message.startswith('course help'):
            return command.HelpCommand()
        else:
            return None

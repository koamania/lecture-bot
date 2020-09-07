import os
import sqlite3

from slacker import Slacker

from bot import Bot
from database import create_connection


def create_bot():
    slack_bot_token = os.environ.get('SLACK_LECTUREBOT_TOKEN')
    slack_api_token = os.environ.get('SLACK_LECTUREAPI_TOKEN')
    # slack_token = 'xoxb-4604786155-902074620452-h8ltmLdtht6TaOMtlVNzATVN'
    return Bot(slack_bot_token, slack_api_token)

def create_database_scheme():
    with create_connection() as conn:
        cur = conn.cursor()
        cur.execute('''
            create table if not exists course_list(
                course_id INTEGER PRIMARY KEY autoincrement ,
                course_name varchar not null,
                status varchar not null,
                user varchar,
                date date
            )
        ''')


if __name__ == '__main__':
    create_database_scheme()
    while True:
        bot = create_bot()
        try:
            bot.run()
        except:
            pass

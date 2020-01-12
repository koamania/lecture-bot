import os
import sqlite3

from slacker import Slacker

from bot import Bot
from database import create_connection


def create_bot():
    slack_bot_token = os.environ.get('LECTUREBOT_SLACK_TOKEN') or 'xoxb-4604786155-902074620452-h8ltmLdtht6TaOMtlVNzATVN'
    slack_api_token = 'xoxp-4604786155-502992257717-902531179184-9d56d2134d127303cde247e26e57a9e7'
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
    bot = create_bot()

    bot.run()

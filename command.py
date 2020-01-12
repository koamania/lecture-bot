import abc
import re
import sqlite3

from database import create_connection


def create_result_message(message: str, pretext: str, title: str):
    attachments_dict = dict()
    attachments_dict['pretext'] = pretext
    attachments_dict['title'] = title
    attachments_dict['text'] = message
    attachments_dict['color'] = '#00ff00'
    attachments_dict['mrkdwn_in'] = ['text', 'pretext']
    return [attachments_dict]


class Command:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def execute(self):
        pass


class List(Command):

    def __init__(self, message: str):
        self._message = message

    def execute(self):
        with create_connection() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute('select * from course_list')
            result = list(cur.fetchall())

            if not result:
                result_text = '등록된 강의가 없습니다.'
            else:
                result_text = '\n'.join([
                    '*{}*\n\t_번호_ : {}, _수강상태_ : {}, _수강자_ : {}, _시작날짜_ : {}'.format(
                        course['course_name'], course['course_id'], '미수강' if course['status'] == 'IDLE' else '수강중',
                        course['user'] or '없음', course['date'] or '없음'
                    ) for course in result
                ])

            return create_result_message(result_text, '강의 목록 조회 결과입니다.', '현재 등록된 강의 목록')


class AddCourse(Command):

    def __init__(self, message: str):
        self._message = message

    def execute(self):
        delimeter_index = [m.start() for m in re.finditer(' ', self._message)]
        course_name = self._message[delimeter_index[1] + 1:]
        with create_connection() as conn:
            cur = conn.cursor()
            cur.execute('insert into course_list(course_name, status) values(?, ?)', (course_name, 'IDLE'))
            conn.commit()
        return create_result_message('강의명 : {}'.format(course_name), '강의 등록 결', '신규강의가 추가되었습니다')


class DeleteCourse(Command):
    def __init__(self, message: str):
        self._message = message

    def execute(self):
        delimeter_index = [m.start() for m in re.finditer(' ', self._message)]
        course_id = int(self._message[delimeter_index[1] + 1:])

        with create_connection() as conn:
            cur = conn.cursor()
            course = cur.execute('select * from course_list where course_id = ?', (course_id,)).fetchone()

            if not course:
                raise Exception('요청하신 강의를 찾을 수 없습니다.')

            cur.execute('delete from course_list where course_id=?', (course_id,))
            conn.commit()
        return create_result_message('강의 번호 : {}번'.format(course_id), '강의 삭제 과결', '강의가 삭제되었습니다')


class StartCourse(Command):

    def __init__(self, message: str, user: str):
        self._message = message
        self._user = user

    def execute(self):
        delimeter_index = [m.start() for m in re.finditer(' ', self._message)]
        course_id = int(self._message[delimeter_index[1] + 1:])

        with create_connection() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            course = cur.execute('select * from course_list where course_id = ?', (course_id,)).fetchone()

            if not course:
                raise Exception('요청하신 강의를 찾을 수 없습니다.')

            if course['status'] == 'STUDYING':
                raise Exception('이미 수강중인 사용자가 있습니다.')

            cur.execute("update course_list set status=?, user=?, date=datetime('now','localtime') where course_id=?",
                        ('STUDYING', self._user, course_id))
            conn.commit()
        return create_result_message('강의 번호 : {}'.format(course_id), '수강 신청 결과', '수강요청 되었습니다')


class EndCourse(Command):

    def __init__(self, message: str):
        self._message = message

    def execute(self):
        delimeter_index = [m.start() for m in re.finditer(' ', self._message)]
        course_id = int(self._message[delimeter_index[1] + 1:])

        with create_connection() as conn:
            cur = conn.cursor()
            course = cur.execute('select * from course_list where course_id = ?', (course_id,)).fetchone()

            if not course:
                raise Exception('요청하신 강의를 찾을 수 없습니다.')

            cur.execute('update course_list set status=?, user=null, date=null where course_id=?',
                        ('IDLE', course_id))
            conn.commit()
        return create_result_message('강의 번호 : {}'.format(course_id), '수강 종 결과', '수강 종료되었습니다')


class HelpCommand(Command):

    def execute(self):
        return create_result_message('''
        동시성 제어는 안되니까 modify 요청은 적당히 눈치봐서...
         
        강의 목록 : _*course list*_
        강의 등록 : _*course add <강의 이름(띄어 쓰기 가능)>*_
        강의 삭제 : _*course delete <강의 번호(목록 조회)>*_
        수강 시작 : _*course start <강의 번호(목록 조회)>*_
        수강 종료 : _*course end <강의 번호(목록 조회)>*_
        ''', '배워서 남주는 봇 도움말', '명령어 목록')

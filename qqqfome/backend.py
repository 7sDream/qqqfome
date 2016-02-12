import time
import datetime
import logging

from . import daemon
from . import db
from . import common as c
from . import strings as s

from zhihu import ZhihuClient


def calc_message(pattern, me, you, new_follower_num):
    offset = datetime.timedelta(hours=8)
    china_now = datetime.datetime.utcnow() + offset
    my_name = me.name
    follower_num = me.follower_num - new_follower_num
    your_name = you.name

    return pattern.format(now=china_now, my_name=my_name,
                          follower_num=follower_num, your_name=your_name)


class BackendCode(daemon.DaemonProcess):
    def at_exit(self):
        pass

    def run(self, database, msg, interval, log_file, max_old=10):
        c.check_type(database, 'database', str)

        L = logging.getLogger('qqqfome-backend')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        sh.setFormatter(formatter)
        L.setLevel(logging.DEBUG)
        L.addHandler(fh)
        L.addHandler(sh)

        try:
            L.info(s.log_connected_to_db.format(database))
            conn = db.connect_db(database)
            L.info(s.success)
        except FileNotFoundError:
            L.exception(s.log_file_not_exist.format(database))
            L.info(s.exit)
            return

        # get cookies from database
        cookies = db.get_cookies(conn)

        if not cookies:
            L.exception(s.log_no_cookies_in_database)
            L.info(s.exit)
            return

        L.info(s.log_get_cookies_from_database)
        L.debug(cookies)

        try:
            client = ZhihuClient(cookies)
            L.info(s.log_build_zhihu_client)
        except Exception as e:
            L.exception(e)
            return

        while True:
            L.info(s.log_start_a_pass)

            try:
                me = client.me()
                L.info(s.log_build_me)
            except Exception as e:
                L.exception(e)
                return

            follower_num = me.follower_num
            L.info(s.log_get_follower_num.format(follower_num))
            db.log_to_db(conn, follower_num, s.log_start_a_pass)

            continue_in_db = 0
            new_follower_num = 0
            for follower in me.followers:
                L.info(s.log_check_follower.format(follower.name, follower.id))
                if db.is_in_db(conn, follower.id):
                    L.info(s.log_follower_in_db.format(follower.id))
                    continue_in_db += 1
                else:
                    L.info(s.log_follower_not_in_db.format(follower.name))
                    continue_in_db = 0

                    L.info(s.log_send_message.format(follower.name))

                    try:
                        message = calc_message(msg, me, follower,
                                               new_follower_num)
                    except Exception as e:
                        L.exception(e)
                        message = msg

                    L.debug(message)

                    i = 0
                    while i < 5:
                        try:
                            me.send_message(follower, message)
                            new_follower_num += 1
                            L.info(s.success)
                            L.info(s.log_add_user_to_db.format(follower.name))
                            db.add_user_to_db(conn, follower)
                            break
                        except Exception as e:
                            L.exception(e)
                            L.debug(s.log_send_failed)
                        i += 1

                if continue_in_db == max_old:
                    L.info(s.log_continue_reach_max.format(max_old))
                    break

            L.info(s.log_finish_a_pass)
            time.sleep(interval)

import argparse
import logging
import os
import sys

from zhihu import ZhihuClient

from . import common as c
from . import strings as s
from . import db
from . import backend

L = logging.getLogger('qqqfome-entry')


def init_db(cookies):
    if cookies is not None:
        c.check_type(cookies, 'cookies', str)

    # login in with cookies file
    if cookies:
        author = ZhihuClient(cookies=cookies).me()
    # login in terminal
    else:
        client = ZhihuClient()

        try:
            cookies = client.login_in_terminal()
        except KeyboardInterrupt:
            print()
            cookies = ''

        if not cookies:
            L.error(s.log_login_failed)
            L.info(s.exit)
            exit(0)

        author = client.me()

    try:
        conn = db.create_db(author)
        db.create_table(conn)
        db.dump_init_data_to_db(conn, author)
        db.close_db(conn)
        print(s.success)
    except FileExistsError as e:
        L.error(s.file_exist.format(e.filename))
        print(s.failed)


class SetDefaultPID(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        default_pid = getattr(namespace, 'pid_file')
        default_log = getattr(namespace, 'log_file')
        try:
            if values:
                filename = os.path.basename(os.path.abspath(values))
                default_pid = default_pid.format(filename)
                default_log = default_log.format(filename)
        except TypeError:
            # pid has already been replaced
            pass
        setattr(namespace, 'pid_file', default_pid)
        setattr(namespace, 'log_file', default_log)


def main():
    parser = argparse.ArgumentParser(prog='qqqfome',
                                     description='Thank-you-follow-me cli.')

    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='count', default=0,
                        help=s.cmd_help_print_info)
    parser.add_argument('-c', '--cookies', dest='cookies', metavar='FILE',
                        help=s.cmd_help_cookies,
                        type=str)
    parser.add_argument('-p', '--pid-file', dest='pid_file', metavar='FILE',
                        help=s.cmd_help_pid_file,
                        type=str, default='{0}.pid')
    parser.add_argument('-l', '--log-file', dest='log_file', metavar='FILE',
                        help=s.cmd_help_log_file,
                        type=str, default='{0}.log')
    parser.add_argument('-t', '--time', dest='time', metavar='INTERVAL',
                        help=s.cmd_help_time,
                        type=int, default=90)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-m', '--message', dest='message',
                       help=s.cmd_help_message,
                       type=str, default=s.default_message)
    group.add_argument('-M', '--message-file', dest='message_file',
                       metavar='FILE',
                       help=s.cmd_help_message,
                       type=str)

    parser.add_argument('-s', '--stop-at', dest='stop_at', metavar='NUM',
                        help=s.cmd_help_stop_at, type=int, default=10)
    parser.add_argument('-d', '--daemon', dest='daemon', action='store_true',
                        default=False, help='work in daemon mode')
    parser.add_argument('command', help=s.cmd_help_command, type=str,
                        choices=['init', 'start', 'stop'])
    parser.add_argument('file', help=s.cmd_help_file, type=str,
                        action=SetDefaultPID, nargs='?')

    args = parser.parse_args()

    # Logger settings
    level = logging.ERROR
    if args.verbose == 1:
        level = logging.INFO
    if args.verbose >= 2:
        level = logging.DEBUG

    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    db.set_logger_level(level)
    db.set_logger_handle(ch)

    L.setLevel(level)
    L.addHandler(ch)

    L.debug(args)

    if args.command == "init":
        init_db(args.cookies)
    elif args.file is None:
            parser.error(s.cmd_help_no_file_error.format(args.command))

    if args.command == 'start':
        if args.message_file is not None:
            with open(args.message_file, 'r') as f:
                args.message = f.read()
        if args.daemon:
            p = backend.BackendCode(args.pid_file)
            try:
                p.start(args.file, args.message, args.time, args.log_file)
            except OSError:     # daemon mode not support the system
                p.run(args.file, args.message, args.time, args.log_file)
        else:
            p = backend.BackendCode(args.pid_file, stdin=sys.stdin,
                                    stdout=sys.stdout, stderr=sys.stderr)
            p.run(args.file, args.message, args.time, args.log_file)
    elif args.command == 'stop':
        try:
            p = backend.BackendCode(args.pid_file)
            p.stop()
        except FileNotFoundError as e:
            L.error(e)


if __name__ == '__main__':
    main()

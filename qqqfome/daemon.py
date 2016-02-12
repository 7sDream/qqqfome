"""
Make some code running in daemon.

Modify from Open Source file:
    https://github.com/serverdensity/python-daemon/blob/master/daemon.py
"""

import os
import sys
import signal
import atexit
import time

from . import common as c
from . import strings as s


class DaemonProcess:
    def __init__(self, pidfile,
                 stdin=os.devnull, stdout=os.devnull, stderr=os.devnull,
                 workdir='.', umask='022'):
        c.check_type(pidfile, 'pidfile', str)
        c.check_type(workdir, 'workdir', str)
        c.check_type(umask, 'umask', str)

        self._pidfile = pidfile
        self._stdin = stdin
        self._stdout = stdout
        self._stderr = stderr
        self._work_dir = workdir
        self._alive = True

        try:
            self.umask = int(umask, base=8)
        except ValueError as e:
            raise ValueError(s.daemon_umask_error)

    def run(self, *args, **kwargs):
        """
        Override me.
        """
        pass

    def at_exit(self):
        """
        Override me.
        """
        pass

    def _write_pid_file(self, pid):
        with open(self._pidfile, 'w', encoding='utf-8') as f:
            f.writelines([str(pid)])

    def _del_pid_file(self):
        self.at_exit()
        os.remove(self._pidfile)

    def get_pid_from_pidfile(self):
        try:
            with open(self._pidfile, 'r', encoding='utf-8') as f:
                return int(f.read().strip())
        except IOError:
            return None
        except SystemExit:
            return None

    def _make_me_daemon(self):
        # first fork
        try:
            pid = os.fork()
            if pid != 0:
                sys.exit(0)
        except OSError as e:
            raise OSError(s.daemon_fork_error.format(e.errno, e.strerror))

        os.setsid()
        os.umask(self.umask)
        os.chdir(self._work_dir)

        # second fork
        try:
            pid = os.fork()
            if pid != 0:
                sys.exit(0)
        except OSError as e:
            raise OSError(s.daemon_fork_error.format(e.errno, e.strerror))

        # redirect streams
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self._stdin, 'r') if isinstance(self._stdin, str) \
            else self._stdin
        so = open(self._stdout, 'a+') if isinstance(self._stdout, str) \
            else self._stdout
        if self._stderr:
            se = open(self._stderr, 'a+') if isinstance(self._stderr, str) \
                else self._stdout
        else:
            se = so
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # set signal handler
        def signal_handler(signum, frame):
            self._alive = False
            exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        pid = os.getpid()
        print(pid)
        atexit.register(self._del_pid_file)
        self._write_pid_file(pid)

    def start_when_pid_file_exist(self):
        raise FileExistsError(
            s.daemon_pid_file_exist_error.format(self._pidfile))

    def start(self, *args, **kwargs):
        if not (sys.platform.startswith('linux') or sys.platform.startswith(
                'darwin')):
            raise OSError(s.daemon_os_error)

        pid = self.get_pid_from_pidfile()

        if pid is not None:
            self.start_when_pid_file_exist()

        self._make_me_daemon()
        self.run(*args, **kwargs)

    def stop_when_pid_file_not_exist(self):
        raise FileNotFoundError(
            s.daemon_pid_file_not_found_error.format(self._pidfile))

    def stop(self):
        pid = self.get_pid_from_pidfile()

        if pid is None:
            # Just to be sure. A ValueError might occur if the PID file is
            # empty but does actually exist
            if os.path.exists(self._pidfile):
                os.remove(self._pidfile)

            self.stop_when_pid_file_not_exist()
        else:
            try:
                i = 0
                while 1:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(0.1)
                    i += 1
                    if i % 10 == 0:
                        os.kill(pid, signal.SIGHUP)
            except OSError as err:
                err = str(err)
                if err.find("No such process") > 0:
                    if os.path.exists(self._pidfile):
                        os.remove(self._pidfile)
                else:
                    raise OSError(s.daemon_can_not_kill_process.format(pid))

    def is_running(self):
        pid = self.get_pid_from_pidfile()

        return self._pid and os.path.exists('/proc/%d' % pid)

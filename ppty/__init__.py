import os
import sys
import signal
import tty
import fcntl
import socket

from ppty.utils import logger
debug = logger.debug


def pty(exeargv, ignoreeof=False, noecho=False,
        interactive=True, driver=None):
    if driver:
        debug("do_driver")
        do_driver(driver)

    interactive = sys.stdin.isatty() and interactive
    if interactive:
        ttyattr = tty.tcgetattr(0)
        # struct winsize 4 unsigned short. see ioctl_tty(2)
        winsize = fcntl.ioctl(0, tty.TIOCGWINSZ, 8 * b' ')
        debug("tty set to raw")
        tty.setraw(0)

    pid, fdm = os.forkpty()
    if pid == 0:
        # python's forkpty can't pass termios and winsize. do manually
        # see forkpty(3)
        if interactive:
            tty.tcsetattr(0, tty.TCSANOW, ttyattr)
            fcntl.ioctl(0, tty.TIOCSWINSZ, winsize)
        else:
            ttyattr = tty.tcgetattr(0)
        if noecho:
            ttyattr[3] = ttyattr[3] & ~tty.ECHO # lflags
            tty.tcsetattr(0, tty.TCSANOW, ttyattr)
        os.execvp(exeargv[0], exeargv)

    debug("do_loop")
    loop(fdm, ignoreeof)

    # only parent get here. restore tty
    if interactive:
        debug("tty set raw back")
        tty.tcsetattr(0, tty.TCSAFLUSH, ttyattr)


def loop(fdm, ignoreeof=False):
    # prevent gabarge collector closing stdin, stdout
    global stdin, stdout
    bufsize = 1024
    # open as binary I/O. buffered and flush method support 
    stdin = os.fdopen(0, 'rb')
    stdout = os.fdopen(1, 'wb')
    pid = os.fork()
    if pid == 0:
        count = 1
        prefix = '\x1b[32;1m---> '
        pid = os.getpid()
        pty = os.fdopen(fdm, 'wb')
        while True:
            # b = stdin.read1(bufsize) can't do this in python2
            try:
                debug("%s(%d) read stdin" % (prefix, count))
                b = os.read(0, bufsize)
                debug("%s(%d) read stdin %r" % (prefix, count, b))
            except Exception as e:
                debug("%s(%d) read stdin error: %s" % (prefix, count, e))
                b = b''
            if b == b'':
                if not ignoreeof:
                    os.write(fdm, b'\x04') # send C-D
                    os.kill(os.getppid(), signal.SIGTERM)
                break
            debug("%s(%d) write pty" % (prefix, count))
            pty.write(b)
            pty.flush()
            debug("%s(%d) write pty  %r" % (prefix, count, b))
            count = count + 1
        exit(0)
    else:
        count = 1
        prefix = '\x1b[33;1m<--- '
        sigcaught = [] # non-local
        def sig_term(signum, frame):
            debug("%s signal caught" % prefix)
            sigcaught.append(1)
        signal.signal(signal.SIGTERM, sig_term)

        pty = os.fdopen(fdm, 'rb')
        while True:
            try:
                # b = pty.read1(bufsize)
                debug("%s(%d) read pty" % (prefix, count))
                b = os.read(fdm, bufsize)
                debug("%s(%d) read pty %r" % (prefix, count, b))
            except Exception as e:
                # closed slave tty may cause EIO.  see read(2) EIO
                debug("%s(%d) read pty error: %s" % (prefix, count, e))
                break
            if b == b'':
                break
            try:
                debug("%s(%d) write stdout" % (prefix, count))
                stdout.write(b)
                stdout.flush()
                debug("%s(%d) write stdout %r" % (prefix, count, b))
            except Exception as e:
                debug("%s(%d) write stdout error: %s" % (prefix, count, e))
                break
            if sigcaught:
                break
            count = count + 1
        if not sigcaught:
            debug("%s kill child" % prefix)
            os.kill(pid, signal.SIGTERM)
        os.waitpid(pid, 0)


def do_driver(driver):
    exeargv = driver.split()
    s0, s1 = socket.socketpair()
    pipe0, pipe1 = s0.fileno(), s1.fileno()
    pid = os.fork()
    if pid == 0:
        os.close(pipe1)
        os.dup2(pipe0, 0)
        os.dup2(pipe0, 1)
        os.close(pipe0)
        os.execvp(exeargv[0], exeargv)

    os.close(pipe0) 
    os.dup2(pipe1, 0)
    os.dup2(pipe1, 1)
    os.close(pipe1)
    # parent return, 
    # but with stdin/stdout connected to dirver

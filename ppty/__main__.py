import argparse
import logging

from ppty import pty
from ppty.utils import logger

def main():
    parser = argparse.ArgumentParser(description='Run process in pseudoterminal')
    parser.add_argument('prog', help='program to run')
    parser.add_argument('args', nargs='*', help='args to the program')
    parser.add_argument('-i', '--ignoreeof', action='store_true', help='ignore EOF on stdin')
    parser.add_argument('-e', '--noecho', action='store_true', help='noecho for slave pty')
    parser.add_argument('-n', '--no-interactive', action='store_false',
                        dest='interactive', help='not interactive')
    parser.add_argument('-d', '--driver', help='driver (executable) for stdin/stdout')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug(args)
    exeargv = [args.prog] + args.args
    pty(exeargv, args.ignoreeof, args.noecho, args.interactive, args.driver)


if __name__ == '__main__':
    main()

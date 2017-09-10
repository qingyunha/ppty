## ppty --  run process in pseudoterminal.
Python implementation of `pty`. ( Chapter 19 of  [APUE](http://www.apuebook.com/)  by W. Richard Stevens.)

Test in Python 3.6 and 2.7 in `4.12.8-2-ARCH GNU/Linux

## Install
```sh
pip install ppty
```

## Usage
```sh
usage: ppty [-h] [-i] [-e] [-n] [-d DRIVER] [-v] prog [args [args ...]]

Run process in pseudoterminal

positional arguments:
  prog                  program to run
  args                  args to the program

optional arguments:
  -h, --help            show this help message and exit
  -i, --ignoreeof       ignore EOF on stdin
  -e, --noecho          noecho for slave pty
  -n, --no-interactive  not interactive
  -d DRIVER, --driver DRIVER
                        driver (executable) for stdin/stdout
  -v, --verbose
```

## Example
```sh
ppty sh
```

```
ppty -i slowout </dev/null >file.out &  # monitor a slow output and long-running program in the background
```

```sh
ppty sh | tee typescript  # simulate scirpt(1)
```

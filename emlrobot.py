import emapp
import sys


if __name__ == '__main__':
    arg = False
    if len(sys.argv) > 1:
        if sys.argv[1] == '-e':
            arg = True
    emapp.emailfunc.mainprocess(arg)

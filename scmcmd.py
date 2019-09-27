import sys
import libscm as scm


def main():
    s = sys.argv[1]
    print(scm.eval(scm.parse(s)))


if __name__ == '__main__':
    main()

import sys
from common.constants import Constants


def main():
    print("Starting server on {}:{}".format(Constants.SERVER_IP, Constants.SERVER_PORT))


if __name__ == '__main__':
    sys.exit(main())

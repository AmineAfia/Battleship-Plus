import sys

from common.constants import Constants
from frontend.welcome import Welcome


def main():
    print("Connecting to server {}:{}".format(Constants.SERVER_IP, Constants.SERVER_PORT))
    welcome = Welcome()
    welcome.main_welcome()


if __name__ == '__main__':
    sys.exit(main())

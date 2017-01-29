import sys

from frontend.welcome import Welcome


def main():
    welcome = Welcome()
    welcome.main_welcome()


if __name__ == '__main__':
    sys.exit(main())

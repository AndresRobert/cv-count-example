# Char colors
C_END = '\033[0m'
C_BLACK = '\33[30m'
C_RED = '\33[31m'
C_GREEN = '\33[32m'
C_YELLOW = '\33[33m'
C_BLUE = '\33[34m'
C_VIOLET = '\33[35m'
C_BEIGE = '\33[36m'
C_WHITE = '\33[37m'

# Background colors
C_BLACK_BG = '\33[40m'
C_RED_BG = '\33[41m'
C_GREEN_BG = '\33[42m'
C_YELLOW_BG = '\33[43m'
C_BLUE_BG = '\33[44m'
C_VIOLET_BG = '\33[45m'
C_BEIGE_BG = '\33[46m'
C_WHITE_BG = '\33[47m'

# Logging format
INFO = C_BLUE + "INFO: {}" + C_END
DEBUG = C_GREEN + "DEBUG: {}" + C_END
WARN = C_YELLOW + "WARN: {}" + C_END
ERROR = C_RED + "ERROR: {}" + C_END

# Logging level
LOG_LEVEL = "DEBUG"


def info(message):
    """
    Prints out the message in INFO level. It's used for full step by step logging
    Arguments:
        message: String
    """
    if LOG_LEVEL in ["INFO"]:
        print(INFO.format(message))


def debug(message):
    """
    Prints out the message in DEBUG and INFO level. It's used to show useful debug information
    Arguments:
        message: String
    """
    if LOG_LEVEL in ["INFO", "DEBUG"]:
        print(DEBUG.format(message))


def warn(message):
    """
    Prints out the message in WARNING, DEBUG and INFO level. It's used to show unexpected behaviour
    Arguments:
        message: String
    """
    if LOG_LEVEL in ["INFO", "DEBUG", "WARN"]:
        print(WARN.format(message))


def error(message):
    """
    Prints out the message in all levels. It's used to show breaking errors
    Arguments:
        message: String
    """
    print(ERROR.format(message))


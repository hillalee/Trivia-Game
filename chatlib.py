# chatlib.py
# Protocol Constants
CMD_FIELD_LENGTH = 16
LENGTH_FIELD_LENGTH = 4
MAX_DATA_LENGTH = 10 ** LENGTH_FIELD_LENGTH - 1
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH
DELIMITER = "|"
DATA_DELIMITER = "#"

# Protocol Messages
PROTOCOL_CLIENT = {
    "login_msg": "LOGIN",
    "logout_msg": "LOGOUT",
    "highscore_msg": "HIGHSCORE",
    "GET_SCORE": "MY_SCORE",
    "GET_QUESTION": "GET_QUESTION",
    "SEND_ANSWER": "SEND_ANSWER",
    "logged_msg": "LOGGED"
}

PROTOCOL_SERVER = {
    "login_ok_msg": "LOGIN_OK",
    "login_failed_msg": "ERROR",
    "loggedlist_msg": "LOGGED_ANSWER",
    "error_msg": "ERROR"
}

ERROR_RETURN = None

def build_message(cmd, data):
    length = len(data)
    if (cmd not in PROTOCOL_CLIENT.values()) or length > MAX_DATA_LENGTH:
        return None
    full_msg = cmd.ljust(16) + DELIMITER + str(length).zfill(4) + DELIMITER + data
    return full_msg

def parse_message(data):
    try:
        data = data.split("|")
        cmd = data[0].replace(" ", "")
        msg = data[-1]
        if int(data[1]) != len(msg):
            return None, None
    except:
        return None, None
    else:
        return cmd, msg

def split_data(msg, expected_fields):
    msg = msg.split(DATA_DELIMITER)
    if len(msg) == expected_fields + 1:
        return msg
    else:
        return [None]

def join_data(msg_fields):
    msg = DATA_DELIMITER.join(msg_fields)
    return msg

class UserNotFound(Exception):
    def __init__(self):
        self._arg = ""

    def __str__(self):
        return "User not found in users."

    def get_arg(self):
        return self._arg

class WrongPassword(Exception):
    def __init__(self):
        self._arg = ""

    def __str__(self):
        return "Wrong password. Please try again."

    def get_arg(self):
        return self._arg

class UnknownCMD(Exception):
    def __init__(self):
        self._arg = ""

    def __str__(self):
        return "Unknown command. Please try again."

    def get_arg(self):
        return self._arg

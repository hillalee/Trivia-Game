##############################################################################
# server.py
##############################################################################

from socket import *
import select, time, random

import chatlib


# GLOBALS
users = {
    "test": {
        "password": "test",
        "score": 0,
        "questions_asked": []
    },
    "abc": {
        "password": "123",
        "score": 0,
        "questions_asked": []
    },
}
questions = {}
logged_users = {}
messages_to_send = []


ERROR_MSG = "Error! "
SERVER_PORT = 5678
SERVER_IP = "127.0.0.1"


# HELPER SOCKET METHODS
def build_and_send_message(conn, cmd, msg=" "):
    # copy from client
    full_msg = chatlib.build_message(cmd, msg)
    conn.send(full_msg.encode())
    print("[SERVER] ", full_msg)  # Debug print
    time.sleep(0.1)


def recv_message_and_parse(conn):
    try:
        full_msg = conn.recv(1024).decode()
        print("[CLIENT] ", full_msg)  # Debug print
        cmd, data = chatlib.parse_message(full_msg)
    finally:
        return cmd, data


# Data Loaders #

def load_questions():
    """
    Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
    Receives: -
    Returns: questions dictionary
    """
    questions = {
        2313: {"question": "How much is 2+2?", "answers": ["3", "4", "2", "1"], "correct": 2},
        4122: {"question": "What is the capital of France?", "answers": ["Lion", "Marseille", "Paris", "Montpelier"],
               "correct": 3},
        1587: {
            "question": "What year was the iPhone first released in?",
            "answers": ["2007", "2009", "2010", "2012"],
            "correct": 1
        },
        9621: {
            "question": "Which video game console, first released in 2006, was the first to use motion controls during gameplay?",
            "answers": ["Sega Megadrive", "Nintendo Wii", "Playstation", "Xbox 360"],
            "correct": 2
        },
        5311: {
            "question": "When was eBay founded?",
            "answers": ["1990", "1995", "2001", "2005"],
            "correct": 2
        },
        6422: {
            "question": "A green owl is the mascot for which app?",
            "answers": ["Spotify", "Tinder", "Duolingo", "WhatsApp"],
            "correct": 3
        },
        7533: {
            "question": "How many times has the Mona Lisa been stolen?",
            "answers": ["One", "Five", "Eight", "Ten"],
            "correct": 1
        },
        8644: {
            "question": "In Ancient Rome, how many days of the week were there?",
            "answers": ["Five", "Six", "Eight", "Ten"],
            "correct": 3
        },
        9755: {
            "question": "What was New York’s original name?",
            "answers": ["New Liverpool", "New Amsterdam", "New Brussels", "New London"],
            "correct": 2
        },
        10866: {
            "question": "In what year did the Titanic sink?",
            "answers": ["1900", "1912", "1921", "1933"],
            "correct": 2
        },
        11977: {
            "question": "Until 1981, Greenland was a colony of which country?",
            "answers": ["France", "Spain", "Denmark", "Norway"],
            "correct": 3
        },
        12088: {
            "question": "How many US presidents have been assassinated?",
            "answers": ["Three", "Four", "Five", "Six"],
            "correct": 2
        },
        13199: {
            "question": "What is the modern name for the island formerly known as Van Diemen’s Land?",
            "answers": ["The Isle of Wight", "Tasmania", "Hawaii", "Falkland Islands"],
            "correct": 2
        },
        14310: {
            "question": "Who was assassinated in New York in 1980?",
            "answers": ["President John F Kennedy", "John Lennon", "Gianni Versace", "Malcolm X"],
            "correct": 2
        },
        15421: {
            "question": "Who painted The Last Supper?",
            "answers": ["Leonardo Da Vinci", "Rembrandt", "Michelangelo", "Vincent van Gogh"],
            "correct": 1
        }
    }

    return questions


def load_user_database():
    """
    Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
    Receives: -
    Returns: user dictionary
    """
    users = {
        "test": {"password": "test", "score": 0, "questions_asked": []},
        "yossi": {"password": "123", "score": 50, "questions_asked": []},
        "master": {"password": "master", "score": 200, "questions_asked": []}
    }
    return users


# SOCKET CREATOR

def setup_socket():
    """
    Creates new listening socket and returns it
    Receives: -
    Returns: the socket object
    """
    sock = socket(AF_INET, SOCK_STREAM)
    try:
        sock.bind((SERVER_IP, SERVER_PORT))
    except OSError:
        print("Try again later")
        exit()
    sock.listen()
    return sock


def send_error(conn, error_msg):
    """
    Send error message with given message
    Receives: socket, message error string from called function
    Returns: None
    """
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["error_msg"], error_msg)


##### MESSAGE HANDLING
def handle_getscore_message(conn, username):
    global users
    score = users[username]["score"]
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["your_score_msg"], str(score))


def handle_highscore_message(conn):
    global users
    scores = [(key, user["score"]) for key, user in users.items()]
    highscore_list = sorted(scores, key=lambda item: item[1], reverse=True)
    highscore = "\n".join(f"{user}: {score}" for user, score in highscore_list)
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["all_score_msg"], "\n"+highscore)


def handle_logged_message(conn):
    global logged_users
    logged_users_list = list(logged_users.values())
    logged_message = ", ".join(logged_users_list)
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["loggedlist_msg"], logged_message)


def handle_logout_message(conn):
    """
    Closes the given socket (in later chapters, also remove user from logged_users dictionary)
    Receives: socket
    Returns: None
    """
    global logged_users
    if conn:
        logged_users.pop(conn)
        conn.close()


def handle_login_message(conn, data):
    """
    Gets socket and message data of login message. Checks  user and pass exists and match.
    If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
    Receives: socket, message code and data
    Returns: None (sends answer to client)
    """
    global users  # This is needed to access the same users dictionary from all functions
    global logged_users  # To be used later

    username, password = chatlib.split_data(data, 1)

    if username in users:
        if users[username]["password"] == password:
            build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_ok_msg"])
            logged_users.update({conn: username})
        else:
            data = "[SERVER] Password Incorrect ..."
            build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_failed_msg"], data)
    else:
        data = "[SERVER] Username not found ..."
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_failed_msg"], data)


def handle_client_message(conn, cmd, data=""):
    """
    Gets message code and data and calls the right function to handle command
    Receives: socket, message code and data
    Returns: None
    """
    global logged_users
    if conn in logged_users.keys():
        if cmd == "LOGOUT":
            handle_logout_message(conn)
        elif cmd == "MY_SCORE":
            handle_getscore_message(conn, logged_users[conn])
        elif cmd == "HIGHSCORE":
            handle_highscore_message(conn)
        elif cmd == "LOGGED":
            handle_logged_message(conn)
        elif cmd == "GET_QUESTION":
            handle_question_message(conn)
        elif cmd == "SEND_ANSWER":
            handle_answer_message(conn, logged_users[conn], data)
        else:
            data = f'[SERVER] The cmd : {cmd} - Not Recognized ...'
            build_and_send_message(conn, chatlib.PROTOCOL_SERVER["error_msg"], data)
    else:
        if cmd == "LOGIN":
            handle_login_message(conn, data)
        else:
            build_and_send_message(conn, chatlib.PROTOCOL_SERVER["error_msg"], "Error occurred during log in.")


def create_random_question():
    global questions
    questions.update(load_questions())

    question_num = random.choice(list(questions.keys()))
    question_data = questions[question_num]

    question = [str(question_num), question_data["question"]]
    question.extend(question_data["answers"])
    question = chatlib.join_data(question)
    return question


def handle_question_message(conn):
    get_question = create_random_question()
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["your_question_msg"], get_question)


def handle_answer_message(conn, username, data):
    global questions, users

    data = chatlib.split_data(data, 1)
    question_number = int(data[0])
    question_answer = int(data[-1])
    correct_answer_index = questions[question_number]["correct"]

    if question_answer == correct_answer_index:
        users[username]["score"] += 5
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["correct_ans_msg"], "Correct Answer!")
    else:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["wrong_ans_msg"], str(correct_answer_index))


def main():
    # Initializes global users and questions dictionaries using load functions, will be used later
    global users
    global questions

    print("Welcome to Trivia Server!")
    sock = setup_socket()
    client_sockets = []
    while True:
        ready_to_read, _, _ = select.select([sock] + client_sockets, [], [])
        for current_socket in ready_to_read:
            if current_socket is sock:
                (client_socket, client_address) = current_socket.accept()
                client_sockets.append(client_socket)
                print("Accepted connection from {}".format(client_address))
            else:
                print("[SERVER] New data from client. {}".format(client_address))
                try:
                    cmd, data = recv_message_and_parse(current_socket)
                    if not cmd:
                        print("Command unknown or data error. Socket terminated by user")
                        print("[SERVER] Ready for new users...")
                        client_sockets.remove(current_socket)
                        current_socket.close()
                    elif cmd == chatlib.PROTOCOL_CLIENT["logout_msg"]:
                        send_error(current_socket,
                                   ("Disconnecting from server, {} ".format(current_socket.getpeername())))
                        handle_logout_message(current_socket)
                        client_sockets.remove(current_socket)
                        current_socket.close()
                        print("[SERVER] User logged out. Ready for new users...")
                    else:
                        print("[CLIENT] ", cmd, data)
                        handle_client_message(current_socket, cmd, data)
                except Exception:
                    print("Exception: Socket terminated by user")
                    print("[SERVER] Ready for new users...")
                    client_sockets.remove(current_socket)
                    current_socket.close()


if __name__ == '__main__':
    main()

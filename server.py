##############################################################################
# server.py
##############################################################################

from socket import *
import select
from typing import List

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
logged_users = {}  # a dictionary of client hostnames to usernames - will be used later

ERROR_MSG = "Error! "
SERVER_PORT = 5678
SERVER_IP = "127.0.0.1"


# HELPER SOCKET METHODS
def build_and_send_message(conn, cmd, msg=" "):
	# copy from client
	full_msg = chatlib.build_message(cmd, msg)
	conn.send(full_msg.encode())
	print("[SERVER] ", full_msg)  # Debug print


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
		2313: {"question": "How much is 2+2", "answers": ["3", "4", "2", "1"], "correct": 2},
		4122: {"question": "What is the capital of France?", "answers": ["Lion", "Marseille", "Paris", "Montpellier"],
			   "correct": 3}
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
	build_and_send_message(conn,chatlib.PROTOCOL_SERVER["error_msg"], error_msg)


##### MESSAGE HANDLING


def handle_getscore_message(conn, username):
	global users
	score = users[username]["score"]
	build_and_send_message(conn, chatlib.PROTOCOL_SERVER["your_score_msg"], "Your score is: " + score)


def handle_highscore_message(conn):
	global users
	score = ((key, user["score"]) for key, user in users.items())
	highscore_list = sorted(list(score), key=lambda item: item[1], reverse=True)
	lis = "\n".join(str(highscore_list))
	build_and_send_message(conn, chatlib.PROTOCOL_SERVER["all_score_msg"], lis)


def handle_logged_message(conn):
	logged = List[logged_users]
	build_and_send_message(conn, chatlib.PROTOCOL_SERVER["loggedlist_msg"], str(logged))



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


def handle_client_message(conn, cmd, data):
	"""
	Gets message code and data and calls the right function to handle command
	Receives: socket, message code and data
	Returns: None
	"""
	global logged_users
	if conn in logged_users.keys():
		if cmd == chatlib.PROTOCOL_CLIENT["logout_msg"]:
			handle_logout_message(conn)
		elif cmd == chatlib.PROTOCOL_CLIENT["my_score_msg"]:
			handle_getscore_message(conn, logged_users[conn])
		elif cmd == chatlib.PROTOCOL_CLIENT["highscore_msg"]:
			handle_highscore_message(conn)
		elif cmd == chatlib.PROTOCOL_CLIENT["logged_msg"]:
			handle_logged_message(conn)
		else:
			data = f'[SERVER] The cmd : {cmd} - Not Recognized ...'
			build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_failed_msg"], data)
	else:
		if cmd == chatlib.PROTOCOL_CLIENT["login_msg"]:
			handle_login_message(conn, data)
		else:
			build_and_send_message(conn, chatlib.PROTOCOL_SERVER["error_msg"], "Error occurred during log in.")


# Implement code ...


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
				print("[SERVER] New data from client.")
				try:
					while True:
						cmd, data = recv_message_and_parse(current_socket)
						if not cmd or not data:
							print("Command unknown or data error. Socket terminated by user")
							print("[SERVER] Ready for new users...")
							client_sockets.remove(current_socket)
							current_socket.close()
							break
						elif cmd == chatlib.PROTOCOL_CLIENT["logout_msg"] or data == "":
							send_error(current_socket, ("Disconnecting from server, {} ".format(current_socket.getpeername())))
							handle_logout_message(current_socket)
							client_sockets.remove(current_socket)
							current_socket.close()
							print("[SERVER] User logged out. Ready for new users...")
							break
						else:
							print("[CLIENT] ", data)
							handle_client_message(current_socket, cmd, data)
				except Exception:
					print("Socket terminated by user")
					print("[SERVER] Ready for new users...")
					client_sockets.remove(current_socket)
					current_socket.close()


if __name__ == '__main__':
	main()

##############################################################################
# server.py
##############################################################################

from socket import *
import select
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
def build_and_send_message(conn, code, msg):
	# copy from client
	full_msg = chatlib.build_message(code, msg)
	conn.send(full_msg.encode())
	print("[SERVER] ", full_msg)  # Debug print


def recv_message_and_parse(conn):
	try:
		full_msg = conn.recv(1024).decode()
		cmd, data = chatlib.parse_message(full_msg)
	except Exception:
		cmd, data = None, None
	finally:
		print("[CLIENT] ", full_msg)  # Debug print
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
	sock.bind((SERVER_IP, SERVER_PORT))
	sock.listen()
	return sock


def send_error(conn, error_msg):
	"""
	Send error message with given message
	Receives: socket, message error string from called function
	Returns: None
	"""
	build_and_send_message(conn, "ERROR", error_msg)


##### MESSAGE HANDLING


def handle_getscore_message(conn, username):
	global users


# Implement this in later chapters


def handle_logout_message(conn):
	"""
	Closes the given socket (in later chapters, also remove user from logged_users dictionary)
	Receives: socket
	Returns: None
	"""
	global logged_users
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

	def handle_login_message(conn, data):
		global users

		username, password = chatlib.split_data(data, 1)
		if username in users:
			if password == users[username]["password"]:
				build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_ok_msg"],
									   "Login successful. Welcome, {}!".format(username))
				logged_users[conn] = username
			else:
				send_error(conn, "Error occurred. Wrong password.")
		else:
			send_error(conn, "Error occurred. Username not found.")


def handle_client_message(conn, cmd, data):
	"""
	Gets message code and data and calls the right function to handle command
	Receives: socket, message code and data
	Returns: None
	"""
	global logged_users  # To be used later
	if cmd == "login_msg":
		handle_login_message(conn, data)
	if cmd == chatlib.PROTOCOL_SERVER["logout"] or "":
		handle_logout_message(conn)
	else:
		send_error(conn, "Error, Unknown command.")


# Implement code ...


def main():
	# Initializes global users and questions dictionaries using load functions, will be used later
	global users
	global questions

	print("Welcome to Trivia Server!")
	sock = setup_socket()
	while True:
		try:
			(client_socket, client_address) = sock.accept()
			print("Accepted connection from {}".format(client_address))
			while True:
				cmd, data = recv_message_and_parse(client_socket)
				if (not cmd) or cmd == chatlib.PROTOCOL_CLIENT["logout_msg"]:
					send_error(client_socket, ("Disconnecting from server, {} ".format(client_socket.getpeername())))
					handle_logout_message(client_socket)
				else:
					handle_client_message(client_socket, cmd, data)
		except KeyboardInterrupt:
			print("Server terminated by user")
			sock.close()
			break
		except Exception as e:
			print(f"An error occurred: {e}")


if __name__ == '__main__':
	main()
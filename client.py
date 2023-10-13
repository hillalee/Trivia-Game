import socket
import chatlib  # To use chatlib functions or consts, use chatlib.****

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5678


# 5678


# HELPER SOCKET METHODS
def build_and_send_message(conn, cmd, data=""):
	"""
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Parameters: conn (socket object), code (str), data (str)
    Returns: Nothing
    """
	msg = chatlib.build_message(cmd, data)
	# print("Server sent: " + msg)
	conn.send(msg.encode())


def recv_message_and_parse(conn):
	"""
    Receives a new message from given socket,
    then parses the message using chatlib.
    Parameters: conn (socket object)
    Returns: cmd (str) and data (str) of the received message.
    If error occurred, will return None, None"""
	full_msg = conn.recv(1024).decode()
	cmd, data = chatlib.parse_message(full_msg)
	return cmd, data


def build_send_recv_parse(conn, cmd, data):
	build_and_send_message(conn, cmd, data)
	cmd, data = recv_message_and_parse(conn)
	return cmd, data


def get_score(conn):
	cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["my_score_msg"], "")
	return "Current score records are: \n" + data


def get_highscore(conn):
	cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["highscore_msg"], "")
	if cmd != "ALL_SCORE":
		return chatlib.ERROR_RETURN
	return "Highscore is: " + data


def play_question(conn):
	cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["get_question_msg"], "")
	if cmd != "YOUR_QUESTION":
		return chatlib.ERROR_RETURN

	msg = chatlib.split_data(data, 5)
	id, question, ans1, ans2, ans3, ans4 = msg[0], msg[1], msg[2], msg[3], msg[4], msg[5]
	print("""Question num. {}: {}\n 
        1. {} \n
        2. {} \n
        3. {} \n
        4. {} """.format(id, question, ans1, ans2, ans3, ans4))
	answer = input("Insert answer, [1-4]: ")
	send_ans = chatlib.join_data([id, answer])

	cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["send_answer_msg"], send_ans)
	if cmd == "CORRECT_ANSWER":
		print("Good job! your answer is correct. \n"
			  "5 points were added to your score.")
	elif cmd == "WRONG_ANSWER":
		print("Wrong. the correct answer is " + data)
	else:
		return chatlib.ERROR_RETURN


def get_logged_users(conn):
	cmd, data = build_send_recv_parse(conn, "LOGGED", "")
	return "Logged users list: \n " + data


def connect():
	gen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	gen_socket.connect((SERVER_IP, SERVER_PORT))
	return gen_socket


def error_and_exit(error_msg):
	print("[Client] Error Message: ", error_msg)
	exit()


def login(conn):
	while True:
		username = input("Please enter username: \n")
		password = input("Please enter password: \n")
		login_pair = chatlib.join_data([username, password])
		build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["login_msg"], login_pair)
		try:
			cmd, data = recv_message_and_parse(conn)
			if cmd == chatlib.PROTOCOL_SERVER["login_ok_msg"] and cmd is not chatlib.ERROR_RETURN:
				print("Login success!")
				break
			else:
				print(data)
		except ConnectionResetError:
			print("Connection to the server was forcibly closed. Exiting.")
			break


def logout(conn):
	build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["logout_msg"], "")
	print("[CLIENT] Logged out.")


def print_cool_menu():
	print(r"""
	->->->->->->->->->->->->->->->->->->->->->

        p         Play a trivia question
        v         View your score
        h         View highscore
        u         View logged users
        q         Quit game
        
	->->->-->->->->->->->->->->->->->->->->->->

    """)


def main():
	gen_socket = connect()
	print("[CLIENT] Server is up.")
	login(gen_socket)
	print(r'''
	
	H i l a ' s
	                  .----.
      .---------. | == |
      |.-"""""-.| |----|
      ||  TRI  || | == |
      |   VIA  || |----|
      |'-.....-'| |::::|
      `"")---(""` |___.|
     /:::::::::::\" _  "
    /:::=======:::\`\`\
    `"""""""""""""`  '-'⠀⠀⠀⠀⠀⠀
	''')
	while True:
		print_cool_menu()
		command = input("Insert command here: 	")
		try:
			if command == "p":
				print(play_question(gen_socket))
			elif command == "v":
				print(get_score(gen_socket))
			elif command == "h":
				print(get_highscore(gen_socket))
			elif command == "u":
				print(get_logged_users(gen_socket))
			elif command == "q":
				break
			else:
				print("Illegal input. Please try again.")
		except Exception:
			error_and_exit("Error occurred.")

	logout(gen_socket)
	gen_socket.close()


if __name__ == '__main__':
	main()

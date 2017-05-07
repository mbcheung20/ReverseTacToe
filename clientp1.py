#Names: Michael Cheung, Jake Tusa, Billy Ko
#Date: 5/7/17
#Purpose: CSE 310 Final Project Client

#This is the client code for Part 1.

#Imports
import sys
from socket import *

#Protocols
OK = "200 OK"
LOGIN = "210 LOGIN"
PLACE = "211 PLACE"
EXIT = "212 EXIT"
WAIT = "213 WAIT"
START = "214 START"
GO = "215 GO"
WON = "216 WON"
LOST = "217 LOST"
TIED = "218 TIED"
NAME = "219 NAME"
LEFT = "220 LEFT"
DISPLAY = "221 DISPLAY"
ERROR = "400 ERROR"

#Global variables
loggedIn = False;

#Main function that initiates the client
def main():
    #If the number of arguments isn't 3, print error statement and exit.
    if(len(sys.argv) != 3):
        print("Error: There must be exactly 2 arguments to Client.py. The first argument must be the name of the machine on which "
              "the server program is running. The second argument must be the port number that the server is listening at.")
        return
    #Can't check the validity of the first argument here. If it is invalid, it will become apparent when trying to connect.
    HOST = sys.argv[1]
    #Try to convert second argument into an integer. If it fails, print error statement and exit.
    try:
        PORT = int(sys.argv[2])
    except ValueError:
        print("Error: The second argument must be the port number that the server is listening at. A port number is an int.")
        return
    #Initialize client socket. Bind socket to the given host and port. If connection fails, print error statement and exit.
    clientSocket = socket(AF_INET, SOCK_STREAM)
    try:
        clientSocket.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Error: The connection to the server specified was refused.")
        return
    #Grab server response to connection attempt, decode it, and split based on whitespace.
    response = clientSocket.recv(1024).decode()
    #If code received is OK, print appropriate statement and move on. If not, print error statement and exit.
    if(response == OK):
        print("Server accepted connection.")
    else:
        print("Error: Server did not accept connection. Closing client.")
        return
    #Loop that runs the client until exit.
    while(True):
        #Grab user input from command line and split it based on whitespace.
        arguments = input("> ").split()
        #If no arguments were given, reprompt the user.
        if(len(arguments) == 0):
            continue
        #If the help command is entered properly, print out the help message.
        elif(arguments[0] == "help" and len(arguments) == 1):
            print("login [String]: This command takes one argument, which is your name. This name will uniquely identify you to the "
                  "server. An example of how to use this command is to input 'login Michael'.\n\n"

                  "place [int]: This command takes one argument, which is an integer between 1 and 9 inclusive. This number identifies "
                  "the cell that you want to occupy with this move. An example of how to use this command is to input 'place 4'.\n\n"

                  "exit: This command takes no arguments. Upon issuing this command, you will exit the server.The only way to use this "
                  "command is to input 'exit'.")
        #If the login command is entered properly
        elif(arguments[0] == "login" and len(arguments) == 2):
            global loggedIn
            if(loggedIn):
                print("You are already logged in.")
                continue
            #Generate the login message and send it to the server.
            loginMessage = LOGIN + " " + arguments[1]
            clientSocket.send(loginMessage.encode())
            #Print out message for user
            print("Attempting to login.")
            #Grab server response and decode it
            response = clientSocket.recv(1024).decode()
            #If login was successful
            if(response == OK):
                #Note that the login was accepted
                loggedIn = True
                print("Login successful.")
                #Grab server responseand decode it
                response = clientSocket.recv(1024).decode()
                #If the game is not ready to play
                if(response == WAIT):
                    print("Game is not ready to play. Please wait.")
                    #Wait for the game to start
                    response = clientSocket.recv(1024).decode()
                    #If the game has started
                    if(response == START):
                        print("Game is starting.")
                        #Wait for the server to send the opponent's name
                        response = clientSocket.recv(1024).decode()
                        #Tokenize the name message
                        tokenized = response.split()
                        #Name protocol concat
                        token = tokenized[0] + " NAME"
                        #If server sent me the name
                        if(token == NAME):
                            #Notify user of the opponent's name
                            print("Your opponent's login ID is: " + tokenized[2])
                        #Wait for the server to send the board state
                        board = clientSocket.recv(1024).decode()
                        #Tokenize the board message
                        tokenized = board.split(' ', 2)
                        #Display protocol concat
                        token = tokenized[0] + " " + tokenized[1]
                        #If server sent me the display
                        if(token == DISPLAY):
                            #Notify the player that the game is starting and print out the board
                            print(tokenized[2])
                        #Grab the server message
                        response = clientSocket.recv(1024).decode()
                        #If the server says to make a move, inform the user and prompt.
                        if(response == GO):
                            print("It is your turn. Make your move.")
                            continue
                elif(response == START):
                    print("Game is starting.")
                    #Wait for the server to send the opponent's name
                    response = clientSocket.recv(1024).decode()
                    #Tokenize the name message
                    tokenized = response.split()
                    token = tokenized[0] + " " + tokenized[1]
                    #If server sent me the name
                    if(token == NAME):
                        #Notify user of the opponent's name
                        print("Your opponent's login ID is: " + tokenized[2])
                    #Wait for the server to send the board state
                    board = clientSocket.recv(1024).decode()
                    #Tokenize the board message
                    tokenized = board.split(' ', 2)
                    token = tokenized[0] + " " + tokenized[1]
                    #If server sent me the display
                    if(token == DISPLAY):
                        #Notify the player that the game is starting and print out the board
                        print(tokenized[2])
                    #Grab the server message
                    response = clientSocket.recv(1024).decode()
                    #Tokenize the message
                    tokenized = response.split()
                    token = tokenized[0] + " " + tokenized[1]
                    #If the server says it is opponent's turn, inform the user.
                    if(token == WAIT):
                        print("Opponent is making his/her move. Wait until it is your turn before inputting any commands.")
                        #Wait for the server to send the updated board state and print it out
                        response = clientSocket.recv(1024).decode()
                        #Tokenize the response
                        tokenized = response.split(' ', 2)
                        token = tokenized[0] + " " + tokenized[1]
                        #If the server sent me the display
                        if(token == DISPLAY):
                            #Tokenize the board message
                            print(tokenized[2])
                            #Wait for server message
                            response = clientSocket.recv(1024).decode()
                            #If the server says to make a move, inform the user and prompt.
                            if(response == GO):
                                print("It is your turn. Make your move.")
                                continue
                        elif(response == LEFT):
                            print("Your opponent left the game. Sorry about that. Please wait while we find you a new opponent.")
                            #Grab response from the server
                            response = clientSocket.recv(1024).decode()
                            #If the code was START
                            if(response == START):
                                print("Game is starting.")
                                #Grab response from the server
                                response = clientSocket.recv(1024).decode()
                                #Tokenize the response
                                tokenized = response.split()
                                token = tokenized[0] + " " + tokenized[1]
                                if(token == NAME):
                                    #Print the name
                                    print("Your opponent's login ID is: " + tokenized[2])
                                    #Grab response from server
                                    response = clientSocket.recv(1024).decode()
                                    tokenized = response.split(' ', 2)
                                    token = tokenized[0] + " " + tokenized[1]
                                    if(token == DISPLAY):
                                        print(tokenized[2])
                                        response = clientSocket.recv(1024).decode()
                                        if(response == GO):
                                            print("It is your turn. Make your move.")
                                            continue
            #If login was not successful
            if(response == ERROR):
                #If client is already loggedIn, print out error message and reprompt.
                if(loggedIn):
                    print("You are already logged in.")
                    continue
                #If client login attempt was denied by server, print out error message and reprompt.
                print("Login attempt was denied. Please select a different username.")
                continue
        #If the place command is entered properly
        elif(arguments[0] == "place" and len(arguments) == 2):
            if(loggedIn == False):
                print("You cannot place a piece yet. You are not logged in and you are not in a game.")
            #Try to obtain integer object using the second argument
            try:
                tileNumber = int(arguments[1])
            #If the second argument is unable to be converted to an integer object
            except ValueError:
                print("Error: The second argument must be an integer between 1 and 9 inclusive.")
                continue
            #Make sure tileNumber is 1 to 9 inclusive
            if(tileNumber < 1 or tileNumber > 9):
                print("Error: The second argument must be an integer between 1 and 9 inclusive.")
                continue
            #Generate place message
            placeMessage = PLACE + " " + arguments[1]
            #Send place message to server
            clientSocket.send(placeMessage.encode())
            #Debug print out
            print("Attempting to place piece.")
            #Receive the response from the server
            response = clientSocket.recv(1024).decode()
            #If move denied
            if(response == ERROR):
                #Inform the user that the move was invalid
                print("Invalid move. Spot on the board is already taken. Make another move.")
                continue
            #If move was accepted
            elif(response == OK):
                print("Your piece was placed.")
                #Wait for the updated board state
                board = clientSocket.recv(1024).decode().split(' ', 2)
                #Display board state
                print(board[2])
                #Catch the wait message from the server
                response = clientSocket.recv(1024).decode()
                #Declare over
                over = False
                #If wait received
                if(response == WAIT):
                    #Inform the user that piece was placed successfully and to wait for his/her next turn.1
                    print("Opponent is making his/her move. Wait until it is your turn before inputting any commands.")
                    #Wait for the updated board state
                    board = clientSocket.recv(1024).decode().split(' ', 2)
                    token = board[0] + " " + board[1]
                    #If the server says that the opponent left, inform the user and wait until new opponent connects
                    if(token == LEFT):
                        print("Your opponent left the game. Sorry about that. Please wait while we find you a new opponent.")
                        #Grab response from the server
                        response = clientSocket.recv(1024).decode()
                        #If the code was START
                        if(response == START):
                            print("Game is starting.")
                            #Grab response from the server
                            response = clientSocket.recv(1024).decode()
                            #Tokenize the response
                            tokenized = response.split()
                            token = tokenized[0] + " " + tokenized[1]
                            if(token == NAME):
                                #Print the name
                                print("Your opponent's login ID is: " + tokenized[2])
                                #Grab response from server
                                response = clientSocket.recv(1024).decode()
                                tokenized = response.split(' ', 2)
                                token = tokenized[0] + " " + tokenized[1]
                                if(token == DISPLAY):
                                    print(tokenized[2])
                                    response = clientSocket.recv(1024).decode()
                                    if(response == GO):
                                        print("It is your turn. Make your move.")
                                        continue
                    #Otherwise
                    else:
                        #Display board state
                        print(board[2])
                        #Wait for next message from the server
                        response = clientSocket.recv(1024).decode()
                        #If game is over and I won
                        if(response == WON):
                            print("The game is over. You won! Congratulations!")
                            over = True
                        #If game is over and I lost
                        elif(response == LOST):
                            print("The game is over. You lost. Better luck next time!")
                            over = True
                        #If game is over and I tied
                        elif(response == TIED) :
                            print("The game ended in a tie.")
                            over = True
                        #If my turn
                        elif(response == GO):
                            print("It is your turn make your move.")
                            continue
                else:
                    #If game is over and I won
                    if(response == WON):
                        print("The game is over. You won! Congratulations!")
                        over = True
                    #If game is over and I lost
                    elif(response == LOST):
                        print("The game is over. You lost. Better luck next time!")
                        over = True
                    #If game is over and I tied
                    elif(response == TIED) :
                        print("The game ended in a tie.")
                        over = True
                #If the game ended
                if(over == True):
                    #Wait until server says game is ready. Decode the response.
                    response = clientSocket.recv(1024).decode()
                    #Server says game is ready
                    if(response == START):
                        #Wait for the board state from the server, decode it, and split it
                        board = clientSocket.recv(1024).decode().split(' ', 2)
                        #Notify the player that the game is ready and print out board
                        print("Next game is starting.")
                        print(board[2])
                        #Wait for whose turn it is
                        response = clientSocket.recv(1024).decode()
                        #Server says it is my turn
                        if(response == GO):
                            print("It is your turn. Make your move.")
                            continue
                        #Server says it is opponent's turn
                        elif(response == WAIT):
                            print("Opponent is making his/her move. Wait until it is your turn before inputting any commands.")
                            #Wait for the updated board state
                            response = clientSocket.recv(1024).decode()
                            #If the server says that the opponent left, inform the user and wait until new opponent connects
                            if(response == LEFT):
                                print("Your opponent left the game. Sorry about that. Please wait while we find you a new opponent.")
                                #Grab response from the server
                                response = clientSocket.recv(1024).decode()
                                #If the code was START
                                if(response == START):
                                    print("Game is starting.")
                                    #Grab response from the server
                                    response = clientSocket.recv(1024).decode()
                                    #Tokenize the response
                                    tokenized = response.split()
                                    token = tokenized[0] + " " + tokenized[1]
                                    if(token == NAME):
                                        #Print the name
                                        print("Your opponent's login ID is: " + tokenized[2])
                                        #Grab response from server
                                        response = clientSocket.recv(1024).decode()
                                        tokenized = response.split(' ', 2)
                                        token = tokenized[0] + " " + tokenized[1]
                                        if(token == DISPLAY):
                                            print(tokenized[2])
                                            response = clientSocket.recv(1024).decode()
                                            if(response == GO):
                                                print("It is your turn. Make your move.")
                                                continue
                            else:
                                board = response.split(' ', 2)
                                #Print out updated board state
                                print(board[2])
                                #Wait for my turn
                                response = clientSocket.recv(1024).decode()
                                #Server says it is my turn
                                if(reponse == GO):
                                    print("It is your turn make your move.")
                                    continue
        #If the exit command is entered properly
        elif(arguments[0] == "exit" and len(arguments) == 1):
            #Generate the exit message
            exitMessage = EXIT
            #Send exit message to server
            clientSocket.send(exitMessage.encode())
            #Print out for debugging
            print("Attempting to exit.")
            #Wait for server response and decode it.
            response = clientSocket.recv(1024).decode()
            #If the server acknowledged the exit message, print out the appropriate message and close the socket.
            if(response == OK):
                #Print out for debugging
                print("Exit acknowledged.")
                print("Exiting now. See you next time!")
                clientSocket.close()
                return
        #If the given command does not match any of the supported commands, print out the error message and reprompt
        else:
            print("Error: Command not recognized. If you are not familiar with the accepted commands, feel free to input 'help' to see "
                  "the available commands, their uses, and how to use them.")

#Calls the main function on execution
if __name__ == "__main__":
    main()

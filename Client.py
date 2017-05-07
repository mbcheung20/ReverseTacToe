#Names: Michael Cheung, Jake Tusa, Billy Ko
#Date: 5/7/17
#Purpose: CSE 310 Final Project Client

#This code satisfies part 1.

#Imports
import sys
from socket import *

#Protocols
OK = "200"
LOGIN = "210"
PLACE = "211"
EXIT = "212"
WAIT = "213"
START = "214"
GO = "215"
WON = "216"
LOST = "217"
TIED = "218"
NAME = "219"
LEFT = "220"
DISPLAY = "221"
ERROR = "400"

#Global variables
PORT = 1337
loggedIn = False;

#TODO: If we have time, figure out how to either block input from the client when it is not the client's turn, or how to grab that
#input with the server and do nothing until it is that client's turn.
#TODO: Make minor changes to protol definitions to fit Yanni Liu's specifications (mainly LOGIN and PLACE)
#TODO: Maybe restructure client so that the order isn't hard coded
#TODO: Handling for exiting mid game and getting re-matched with someone

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
        portNumber = int(sys.argv[2])
    except ValueError:
        print("Error: The second argument must be the port number that the server is listening at. A port number is an int.")
        return
    #If the given port number doesn't match the required port number, print errror statement and exit.
    if(portNumber != PORT):
        print("Error: The second argument must be the number '1337'. This is the designated port that the server is listening at.")
        return
    #Initialize client socket. Bind socket to the given host and port. If connection fails, print error statement and exit.
    clientSocket = socket(AF_INET, SOCK_STREAM)
    try:
        clientSocket.connect((HOST, PORT))
    except ConnectionRefusedError:
        print("Error: The connection to the server specified was refused. Your first argument seems to have been invalid. Closing client.")
        return
    #Grab server response to connection attempt, decode it, and split based on whitespace.
    tokenized = clientSocket.recv(1024).decode().split()
    #If code received is OK, print appropriate statement and move on. If not, print error statement and exit.
    if(tokenized[0] == OK):
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
            print("help: This command takes no arguments. It prints out all commands available, a brief descriptions "
                  "of each of them, and the syntax of their usage. The only way to use this command is to input 'help'.\n\n"

                  "login [string]: This command takes one argument, which is your name. This name will uniquely identify you to the "
                  "server. An example of how to use this command is to input 'login Michael'.\n\n"

                  "place [int]: This command takes one argument, which is an integer between 1 and 9 inclusive. This number identifies "
                  "the cell that you want to occupy with this move. An example of how to use this command is to input 'place 4'.\n\n"

                  "exit: This command takes no arguments. Upon issuing this command, you will exit the server. You may issue this command "
                  "whenever you want. The only way to use this command is to input 'exit'.")
        #If the login command is entered properly
        elif(arguments[0] == "login" and len(arguments) == 2):
            #Generate the login message and send it to the server.
            loginMessage = LOGIN + " " + arguments[1]
            clientSocket.send(loginMessage.encode())
            #Print out for debugging
            print("Login message sent to server. Login message was: '" + loginMessage + "'")
            #Grab server response and decode it
            response = clientSocket.recv(1024).decode()
            #Print out for debugging
            print("SERVER RESPONSE: " + response)
            #Tokenize the server response
            tokenized = response.split()
            #If login was successful
            if(tokenized[0] == OK):
                #Note that the login was accepted
                global loggedIn
                loggedIn = True
                #Grab server response and decode it
                response = clientSocket.recv(1024).decode()
                #Print out for debugging
                print("SERVER RESPONSE: " + response)
                #Tokenize the server response
                tokenized = response.split()
                #If the game is not ready to play
                if(tokenized[0] == WAIT):
                    #Wait for the game to start
                    response = clientSocket.recv(1024).decode()
                    #Print out for debugging
                    print("SERVER RESPONSE: " + response)
                    #Tokenize the server message
                    tokenized = response.split()
                    #If the game has started
                    if(tokenized[0] == START):
                        #Wait for the server to send the opponent's name
                        response = clientSocket.recv(1024).decode()
                        #Print out for debugging
                        print("SERVER RESPONSE: " + response)
                        #Tokenize the name message
                        tokenized = response.split()
                        #If server sent me the name
                        if(tokenized[0] == NAME):
                            #Notify user of the opponent's name
                            print("Your opponent's login ID is: " + tokenized[2])
                        #Wait for the server to send the board state
                        board = clientSocket.recv(1024).decode()
                        #Print out for debugging
                        print("SERVER RESPONSE: " + board)
                        #Tokenize the board message
                        tokenized = board.split(' ', 2)
                        print(tokenized[0])
                        #If server sent me the display
                        if(tokenized[0] == DISPLAY):
                            #Notify the player that the game is starting and print out the board
                            print("Game is starting.")
                            print(tokenized[2])
                        #Grab the server message
                        response = clientSocket.recv(1024).decode()
                        #Print out for debugging
                        print("SERVER RESPONSE: " + response)
                        #Tokenize the message
                        tokenized = response.split()
                        #If the server says to make a move, inform the user and prompt.
                        if(tokenized[0] == GO):
                            print("It is your turn. Make your move.")
                            continue
                        #If the server says it is opponent's turn, inform the user.
                        elif(tokenized[0] == WAIT):
                            print("Opponent is making his/her move. Wait until it is your turn before inputting any commands.")
                            #Wait for the server to send the updated board state and print it out
                            board = clientSocket.recv(1024).decode()
                            #Print out for debugging
                            print("SERVER RESPONSE: " + board)
                            #Tokenize the board message
                            tokenized = board.split(' ', 2)
                            #If the server sent me the display
                            if(tokenized[0] == DISPLAY):
                                print(tokenized[2])
                            #Wait for server message
                            response = clientSocket.recv(1024).decode()
                            #Print out for debugging
                            print("Response from server: " + response)
                            #Tokenize the server message
                            tokenized = response.split()
                            #If the server says to make a move, inform the user and prompt.
                            if(tokenized[0] == GO):
                                print("It is your turn. Make your move.")
                                continue
                            #TODO: If the server says that the opponent left, inform the user and wait until new opponent connects
                            elif(tokenized[0] == LEFT):
                                print("Your opponent left the game. Sorry about that. Please wait while we find you a new opponent.")
                                #Grab response from the server
                                response = clientSocket.recv(1024).decode()
                                #Print for debugging
                                print(response)
                                #Tokenize the response
                                tokenized = response.split()
                                #If the code was START
                                if(tokenized[0] == START):
                                    print("Game is starting. Get ready!")
                                    #Grab response from the server
                                    response =clientSocket.recv(1024).decode()
                                    #print for Debugging
                                    print(response)
                                    #Tokenize the response
                                    tokenized = response.split()
                                    if(tokenized[0] == NAME):
                                        #Print the name
                                        print("Your opponent's login ID is: " + tokenized[2])
                                        #Grab response from server
                                        response = clientSocket(1024).decode()
                                        tokenized = response.split(' ', 2)
                                        if(tokenized[0] == BOARD):
                                            print(tokenized[2])
                                            response = clientSocket(1024).decode()
                                            tokenized = response.split(' ', 2)
                                            if(tokenized[0] == GO):
                                                print("It is your turn. Make your move.")
                                                continue
                                            if(tokenized[0] == WAIT):
                                                print("Opponent is making his/her move. Wait until it is your turn before inputting any commands.")
                                                #Wait for the server to send the updated board state and print it out
                                                board = clientSocket.recv(1024).decode()
                                                #Print out for debugging
                                                print("SERVER RESPONSE: " + board)
                                                #Tokenize the board message
                                                tokenized = response.split(' ', 2)
                                                #If the server sent me the display
                                                if(tokenized[0] == DISPLAY):
                                                    print(tokenized[2])
                                                #Wait for server message
                                                response = clientSocket.recv(1024).decode()
                                                #Print out for debugging
                                                print("Response from server: " + response)
                                                #Tokenize the server message
                                                tokenized = response.split()
                elif(tokenized[0] == START):
                    #Wait for the server to send the opponent's name
                    response = clientSocket.recv(1024).decode()
                    #Print out for debugging
                    print("SERVER RESPONSE: " + response)
                    #Tokenize the name message
                    tokenized = response.split()
                    #If server sent me the name
                    if(tokenized[0] == NAME):
                        #Notify user of the opponent's name
                        print("Your opponent's login ID is: " + tokenized[2])
                    #Wait for the server to send the board state
                    board = clientSocket.recv(1024).decode()
                    #Print out for debugging
                    print("SERVER RESPONSE: " + board)
                    #Tokenize the board message
                    tokenized = board.split(' ', 2)
                    #If server sent me the display
                    if(tokenized[0] == DISPLAY):
                        #Notify the player that the game is starting and print out the board
                        print("Game is starting.")
                        print(tokenized[2])
                    #Grab the server message
                    response = clientSocket.recv(1024).decode()
                    #Print out for debugging
                    print("SERVER RESPONSE: " + response)
                    #Tokenize the message
                    tokenized = response.split()
                    #If the server says to make a move, inform the user and prompt.
                    if(tokenized[0] == GO):
                        print("It is your turn. Make your move.")
                        continue
                    #If the server says it is opponent's turn, inform the user.
                    elif(tokenized[0] == WAIT):
                        print("Opponent is making his/her move. Wait until it is your turn before inputting any commands.")
                        #Wait for the server to send the updated board state and print it out
                        response = clientSocket.recv(1024).decode()

                        tokenized = response.split(' ', 2)
                        #Print out for debugging
                        print("SERVER RESPONSE: " + response)
                        #If the server sent me the display
                        if(tokenized[0] == DISPLAY):
                            #Tokenize the board message
                            print(tokenized[2])
                            #Wait for server message
                            response = clientSocket.recv(1024).decode()
                            #Print out for debugging
                            print("Response from server: " + response)
                            #Tokenize the server message
                            tokenized = response.split()
                            #If the server says to make a move, inform the user and prompt.
                            if(tokenized[0] == GO):
                                print("It is your turn. Make your move.")
                                continue
                        #TODO: If the server says that the opponent left, inform the user and wait until new opponent connects
                        elif(tokenized[0] == LEFT):
                            print("Your opponent left the game. Sorry about that. Please wait while we find you a new opponent.")
                            #Grab response from the server
                            response = clientSocket.recv(1024).decode()
                            #Print for debugging
                            print(response)
                            #Tokenize the response
                            tokenized = response.split()
                            #If the code was START
                            if(tokenized[0] == START):
                                print("Game is starting. Get ready!")
                                #Grab response from the server
                                response =clientSocket.recv(1024).decode()
                                #print for Debugging
                                print(response)
                                #Tokenize the response
                                tokenized = response.split()
                                if(tokenized[0] == NAME):
                                    #Print the name
                                    print("Your opponent's login ID is: " + tokenized[2])
                                    #Grab response from server
                                    response = clientSocket.recv(1024).decode()
                                    tokenized = response.split(' ', 2)
                                    if(tokenized[0] == DISPLAY):
                                        print(tokenized[2])
                                        response = clientSocket.recv(1024).decode()
                                        tokenized = response.split(' ', 2)
                                        if(tokenized[0] == GO):
                                            print("It is your turn. Make your move.")
                                            continue
                                        if(tokenized[0] == WAIT):
                                            print("Opponent is making his/her move. Wait until it is your turn before inputting any commands.")
                                            #Wait for the server to send the updated board state and print it out
                                            board = clientSocket.recv(1024).decode()
                                            #Print out for debugging
                                            print("SERVER RESPONSE: " + board)
                                            #Tokenize the board message
                                            tokenized = response.split(' ', 2)
                                            #If the server sent me the display
                                            if(tokenized[0] == DISPLAY):
                                                print(tokenized[2])
                                            #Wait for server message
                                            response = clientSocket.recv(1024).decode()
                                            #Print out for debugging
                                            print("Response from server: " + response)
                                            #Tokenize the server message
                                            tokenized = response.split()

            #If login was not successful
            if(tokenized[0] == ERROR):
                #If client is already loggedIn, print out error message and reprompt.
                if(loggedIn):
                    print("You are already logged in.")
                    continue
                #If client login attempt was denied by server, print out error message and reprompt.
                print("Login attempt was denied. Please select a different username.")
                continue
        #If the place command is entered properly
        elif(arguments[0] == "place" and len(arguments) == 2):
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
            print("Place message sent to server. Place message was: '" + placeMessage + "'")
            #Receive the response from the server
            response = clientSocket.recv(1024).decode()
            #Debug print out
            print("Response from server: " + response)
            #Tokenize
            tokenized = response.split()
            #If move denied
            if(tokenized[0] == ERROR):
                #Inform the user that the move was invalid
                print("Invalid move. Spot on the board is already taken. Make another move.")
                continue
            #If move was accepted
            elif(tokenized[0] == OK):
                #Wait for the updated board state
                board = clientSocket.recv(1024).decode().split(' ', 2)
                #Display board state
                print(board[2])
                #Catch the wait message from the server
                response = clientSocket.recv(1024).decode()
                #Debug print out
                print("SERVER RESPONSE: " + response)
                #Tokenize the wait message
                tokenized = response.split()
                #If wait received
                if(tokenized[0] == WAIT):
                    #Inform the user that piece was placed successfully and to wait for his/her next turn.1
                    print("Your piece was placed.")
                    print("Opponent is making his/her move. Wait until it is your turn before inputting any commands.")
                    #Wait for the updated board state
                    board = clientSocket.recv(1024).decode().split(' ', 2)
                    #TODO: If the server says that the opponent left, inform the user and wait until new opponent connects
                    if(board[0] == LEFT):
                            print("Your opponent left the game. Sorry about that. Please wait while we find you a new opponent.")
                            #Grab response from the server
                            response = clientSocket.recv(1024).decode()
                            #Print for debugging
                            print(response)
                            #Tokenize the response
                            tokenized = response.split()
                            #If the code was START
                            if(tokenized[0] == START):
                                print("Game is starting. Get ready!")
                                #Grab response from the server
                                response =clientSocket.recv(1024).decode()
                                #print for Debugging
                                print(response)
                                #Tokenize the response
                                tokenized = response.split()
                                if(tokenized[0] == NAME):
                                    #Print the name
                                    print("Your opponent's login ID is: " + tokenized[2])
                                    #Grab response from server
                                    response = clientSocket.recv(1024).decode()
                                    tokenized = response.split(' ', 2)
                                    if(tokenized[0] == DISPLAY):
                                        print(tokenized[2])
                                        response = clientSocket.recv(1024).decode()
                                        tokenized = response.split(' ', 2)
                                        if(tokenized[0] == GO):
                                            print("It is your turn. Make your move.")
                                            continue
                                        if(tokenized[0] == WAIT):
                                            print("Opponent is making his/her move. Wait until it is your turn before inputting any commands.")
                                            #Wait for the server to send the updated board state and print it out
                                            board = clientSocket.recv(1024).decode()
                                            #Print out for debugging
                                            print("SERVER RESPONSE: " + board)
                                            #Tokenize the board message
                                            tokenized = response.split(' ', 2)
                                            #If the server sent me the display
                                            if(tokenized[0] == DISPLAY):
                                                print(tokenized[2])
                                            #Wait for server message
                                            response = clientSocket.recv(1024).decode()
                                            #Print out for debugging
                                            print("Response from server: " + response)
                                            #Tokenize the server message
                                            tokenized = response.split()
                    #Display board state
                    print(board[2])
                    #Wait for next message from the server
                    response = clientSocket.recv(1024).decode()
                    #Print for debugging
                    print("SERVER RESPONSE:" + response)
                    #Tokenize
                    tokenized = response.split()
                    #Declare boolean for whether game ended or not
                    over = False
                    #If game is over and I won
                    if(tokenized[0] == WON):
                        print("The game is over. You won! Congratulations!")
                        over = True
                    #If game is over and I lost
                    elif(tokenized[0] == LOST):
                        print("The game is over. You lost. Better luck next time!")
                        over = True
                    #If game is over and I tied
                    elif(tokenized[0] == TIED) :
                        print("The game ended in a tie.")
                        over = True
                    #If my turn
                    elif(tokenized[0] == GO):
                        print("It is your turn make your move.")
                        continue
                    #If opponent left

                else:
                    #Declare boolean for whether game ended or not
                    over = False
                    #If game is over and I won
                    if(tokenized[0] == WON):
                        print("The game is over. You won! Congratulations!")
                        over = True
                    #If game is over and I lost
                    elif(tokenized[0] == LOST):
                        print("The game is over. You lost. Better luck next time!")
                        over = True
                    #If game is over and I tied
                    elif(tokenized[0] == TIED) :
                        print("The game ended in a tie.")
                        over = True
                #If the game ended
                if(over == True):
                    #Wait until server says game is ready. Decode the response.
                    response = clientSocket.recv(1024).decode()
                    #Debug print out
                    print("Response from server: " + response)
                    #Tokenize
                    tokenized = response.split()
                    #Server says game is ready
                    if(tokenized[0] == START):
                        #Wait for the board state from the server, decode it, and split it
                        board = clientSocket.recv(1024).decode().split(' ', 2)
                        #Notify the player that the game is ready and print out board
                        print("Next game is starting.")
                        print(board[2])
                        #Wait for whose turn it is
                        response = clientSocket.recv(1024).decode()
                        #Debug print out
                        print("Response from server: " + response)
                        #Tokenize
                        tokenized = response.split()
                        #Server says it is my turn
                        if(tokenized[0] == GO):
                            print("It is your turn. Make your move.")
                            continue
                        #Server says it is opponent's turn
                        elif(tokenized[0] == WAIT):
                            print("Opponent is making his/her move. Wait until it is your turn before inputting any commands.")
                            #Wait for the updated board state
                            board = clientSocket.recv(1024).decode().split(' ', 2)
                            #Print out updated board state
                            print(board[2])
                            #Wait for my turn
                            response = clientSocket.recv(1024).decode()
                            #Debug print out
                            print("Response from server: " + response)
                            #Tokenize
                            tokenized = response.split()
                            #Server says it is my turn
                            if(tokenized[0] == GO):
                                print("It is your turn make your move.")
                                continue
                            elif(tokenized[0] == LEFT):
                                print("Your opponent left the game. Sorry about that.")
                                continue
        #If the exit command is entered properly
        elif(arguments[0] == "exit" and len(arguments) == 1):
            #Generate the exit message
            exitMessage = EXIT
            #Send exit message to server
            clientSocket.send(exitMessage.encode())
            #Print out for debugging
            print("Exit message sent to server. Exit message was: '" + exitMessage + "'")
            #Wait for server response and decode it.
            response = clientSocket.recv(1024).decode()
            #Print ouf for debugging
            print("SERVER RESPONSE: " + response)
            #Tokenize the response
            tokenized = response.split()
            #If the server acknowledged the exit message, print out the appropriate message and close the socket.
            if(tokenized[0] == OK):
                #Print out for debugging
                print("SERVER RESPONSE: Server acknowledged exit.")
                print("Exiting. See you next time!")
                clientSocket.close()
                return
        #If the given command does not match any of the supported commands, print out the error message and reprompt
        else:
            print("Error: Command not recognized. If you are not familiar with the accepted commands, feel free to input 'help' to see "
                  "the available commands, their uses, and how to use them.")

#Calls the main function on execution
if __name__ == "__main__":
    main()

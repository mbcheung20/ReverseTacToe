#Michael Cheung
#Jake Tusa
#Billy Ko

#This is the client code.
#Part 1

#Imports
import sys
from socket import *

#Global variables
PORT = 1337

#Protocols
OK = "200"
LOGIN = "210"
PLACE = "211"
EXIT = "212"
WAIT = "213"
START = "214"
READY = "215"
WON = "216"
LOST = "217"
TIED = "218"
NAME = "219"
LEFT = "220"
DISPLAY = "221"
ERROR = "400"

#Main function that initiates the client
def main():
    #Checks that number of arguments is exactly 3
    if(len(sys.argv) != 3):
        print("Error: There must be exactly 2 arguments to Client.py. The first argument must be the name of the machine on which "
              "the server program is running. The second argument must be the port number that the server is listening at.")
        return
    #Can't check the validity of the first argument here. If it is invalid, it will become apparent when trying to connect.
    HOST = sys.argv[1]
    #Try to obtain integer object using the second argument
    try:
        portNumber = int(sys.argv[2])
    #If the second argument is unable to be converted to an integer object
    except ValueError:
        print("The second argument must be the port number that the server is listening at. A port number is an int.")
        return
    #Checks if the given port number matches the required port number
    if(portNumber != PORT):
        print("Error: The second argument must be the number '1337'. This is the designated port that the server is listening at.")
        return
    #Initialize client socket
    clientSocket = socket(AF_INET, SOCK_STREAM)
    #Try to bind socket to the given host and port
    try:
        clientSocket.connect((HOST, PORT))
    #If connection fails, close client socket
    except ConnectionRefusedError:
        print("The connection to the server specified was refused. Your first argument seems to have been invalid.")
        return
    #Wait for server response. Decode the response. Tokenize.
    tokenized = clientSocket.recv(1024).decode().split()
    #Check if response is 200 OK
    if(tokenized[0] == OK):
        print("Server accepted connection.")
    else:
        print("Server did not accept connection. Closing client.")
        return
    #Continuously run the client prompt until exit
    while(True):
        #Grab user input from command line
        userInput = input("> ")
        #Split user input based on whitespace
        arguments = userInput.split()
        #If no arguments, skip this iteration and reprompt
        if(len(arguments) == 0):
            continue
        #If help command given, print help message block
        elif(arguments[0] == "help" and len(arguments) == 1):
            print("help: This command takes no arguments. It prints out all commands available, a brief descriptions "
                  "of each of them, and the syntax of their usage. The only way to use this command is to input 'help'.\n\n"

                  "login [string]: This command takes one argument, which is your name. This name will uniquely identify you to the "
                  "server. An example of how to use this command is to input 'login Michael'.\n\n"

                  "place [int]: This command takes one argument, which is an integer between 1 and 9 inclusive. This number identifies "
                  "the cell that you want to occupy with this move. An example of how to use this command is to input 'place 4'.\n\n"

                  "exit: This command takes no arguments. Upon issuing this command, you will exit the server. You may issue this command "
                  "whenever you want. The only way to use this command is to input 'exit'.")
        #If login command given
        elif(arguments[0] == "login" and len(arguments) == 2):
            #Generate login message
            loginMessage = LOGIN + " " + arguments[1]
            #Send login message to server
            clientSocket.send(loginMessage.encode())
            #Debug print out
            print("Login message sent to server. Login message was: '" + loginMessage + "'")
            #Wait and receive response from the server. Decode it.
            response = clientSocket.recv(1024).decode()
            #Debug print out
            print("Response from server: " + response)
            #Tokenize
            tokenized = response.split()
            #If login was accepted
            if(tokenized[0] == OK):
                #Wait and receive response from the server. Decode it.
                response = clientSocket.recv(1024).decode()
                #Debug print out
                print("Response from server: " + response)
                #Tokenize
                tokenized = response.split()
                #If game is not ready to play
                if(tokenized[0] == WAIT):
                    #Wait until server says game is ready. Decode the response.
                    response = clientSocket.recv(1024).decode()
                    #Debug print out
                    print("Response from server: " + response)
                    #Tokenize
                    tokenized = response.split()
                    #Server says game is ready
                    if(tokenized[0] == START):
                        #Wait for the player name from the server
                        response = clientSocket.recv(1024).decode()
                        #Debug print out
                        print("Response from server: " + response)
                        #Tokenize
                        tokenized = response.split()
                        #Server gave me the name
                        if(tokenized[0] == NAME):
                            #Notify the player of the opponent's name
                            print("Your opponent's login ID is: " + tokenized[1])
                        #Wait for the board state from the server
                        response = clientSocket.recv(1024).decode()
                        #Debug print out
                        print("Response from server: " + response)
                        #Tokenize
                        tokenized = response.split()
                        #Server gave me the display
                        if(tokenized[0] == DISPLAY):
                            #Notify the player that the game is ready and print out board
                            print("Game is starting.")
                            #Print out the display
                            print(tokenized[1])
                        #Wait for whose turn it is
                        response = clientSocket.recv(1024).decode()
                        #Debug print out
                        print("Response from server: " + response)
                        #Tokenize
                        tokenized = response.split()
                        #Server says it is my turn
                        if(tokenized[0] == READY):
                            print("It is your turn. Make your move.")
                            continue
                        #Server says it is opponent's turn
                        elif(tokenized[0] == WAIT):
                            print("Opponent is making his/her move.")
                            #Wait for the updated board state
                            board = clientSocket.recv(1024).decode()
                            #Print out updated board state
                            print(board)
                            #Wait for my turn
                            response = clientSocket.recv(1024).decode()
                            #Debug print out
                            print("Response from server: " + response)
                            #Tokenize
                            tokenized = response.split()
                            #Server says it is my turn
                            if(tokenized[0] == READY):
                                print("It is your turn make your move.")
                                continue
                            elif(tokenized[0] == LEFT):
                                print("Your opponent left the game. Sorry about that.")
                                continue
                #If game is ready to play
                if(tokenized[0] == START):
                    #Wait for the player name from the server
                    response = clientSocket.recv(1024).decode()
                    #Debug print out
                    print("Response from server: " + response)
                    #Tokenize
                    tokenized = response.split()
                    #Server gave me the name
                    if(tokenized[0] == NAME):
                        #Notify the player of the opponent's name
                        print("Your opponent's login ID is: " + tokenized[1])
                    #Wait for the board state from the server
                    response = clientSocket.recv(1024).decode()
                    #Debug print out
                    print("Response from server: " + response)
                    #Tokenize
                    tokenized = response.split()
                    #Server gave me the display
                    if(tokenized[0] == DISPLAY):
                        #Notify the player that the game is ready and print out board
                        print("Game is starting.")
                        #Print out the display
                        print(tokenized[1])
                    #Wait for whose turn it is
                    response = clientSocket.recv(1024).decode()
                    #Debug print out
                    print("Response from server: " + response)
                    #Tokenize
                    tokenized = response.split()
                    #Server says it is my turn
                    if(tokenized[0] == READY):
                        print("It is your turn. Make your move.")
                        continue
                    #Server says it is opponent's turn
                    elif(tokenized[0] == WAIT):
                        print("Opponent is making his/her move.")
                        #Wait for the updated board state
                        board = clientSocket.recv(1024).decode()
                        #Print out updated board state
                        print(board)
                        #Wait for my turn
                        response = clientSocket.recv(1024).decode()
                        #Debug print out
                        print("Response from server: " + response)
                        #Tokenize
                        tokenized = response.split()
                        #Server says it is my turn
                        if(tokenized[0] == READY):
                            print("It is your turn make your move.")
                            continue
                        elif(tokenized[0] == LEFT):
                            print("Your opponent left the game. Sorry about that.")
                            continue
            #If login was not accepted
            if(tokenized[0] == ERROR):
                #Inform the user that login was denied
                print("Login attempt was denied. Please select a different username.")
                continue
        #If place command given
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
            print(
                "Response from server: " + response
            )
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
                board = clientSocket.recv(1024).decode()
                #Display board state
                print(board)
                #Wait for the next server message
                response = clientSocket.recv(1024).decode()
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
                elif(tokenized[0] == READY):
                    print("It is your turn make your move.")
                    continue
                #If opponent left
                elif(tokenized[0] == LEFT):
                    print("Your opponent left the game. Sorry about that.")
                    continue
                if(over == True):
                    #Wait until server says game is ready. Decode the response.
                    response = clientSocket.recv(1024).decode()
                    #Debug print out
                    print("Response from server: " + response)
                    #Tokenize
                    tokenized = response.split()
                    #Server says game is ready
                    if(tokenized[0] == START):
                        #Wait for the board state from the server
                        board = clientSocket.recv(1024).decode()
                        #Notify the player that the game is ready and print out board
                        print("Game is starting.")
                        print(board)
                        #Wait for whose turn it is
                        response = clientSocket.recv(1024).decode()
                        #Debug print out
                        print("Response from server: " + response)
                        #Tokenize
                        tokenized = response.split()
                        #Server says it is my turn
                        if(tokenized[0] == READY):
                            print("It is your turn. Make your move.")
                            continue
                        #Server says it is opponent's turn
                        elif(tokenized[0] == WAIT):
                            print("Opponent is making his/her move.")
                            #Wait for the updated board state
                            board = clientSocket.recv(1024).decode()
                            #Print out updated board state
                            print(board)
                            #Wait for my turn
                            response = clientSocket.recv(1024).decode()
                            #Debug print out
                            print("Response from server: " + response)
                            #Tokenize
                            tokenized = response.split()
                            #Server says it is my turn
                            if(tokenized[0] == READY):
                                print("It is your turn make your move.")
                                continue
                            elif(tokenized[0] == LEFT):
                                print("Your opponent left the game. Sorry about that.")
                                continue
        #If exit command given
        elif(arguments[0] == "exit" and len(arguments) == 1):
            #Generate exit message
            exitMessage = EXIT
            #Send exit message to server
            clientSocket.send(exitMessage.encode())
            #Debug print out
            print("Exit message sent to server. Exit message was: '" + exitMessage + "'")
            #Wait for server response
            response = clientSocket.recv(1024).decode()
            #Debug print out
            print("Response from server: " + response)
            #Tokenize
            tokenized = response.split()
            #Server acknowledges my exit
            if(tokenized[0] == OK):
                print("Server acknowledged exit.")
            #Close the socket
            clientSocket.close()
            print("Exiting. See you next time!")
            return
        #If given command line argument does not match any of the expected commands
        else:
            print("Error: Command not recognized. If you are not familiar with the accepted commands, feel free to input 'help' to see "
                  "the available commands, their uses, and how to use them.")

#Calls the main function on execution
if __name__ == "__main__":
    main()

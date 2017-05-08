#Names: Michael Cheung, Jake Tusa, Billy Ko
#Date: 5/7/17
#Purpose: CSE 310 Final Project Client

#This code satisfies part 1.

#Imports
import sys
from socket import *
import selectors
from time import sleep

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
WHO = "222 WHO"
GAMES = "223 GAMES"
PLAY = "224 PLAY"
MATCHED = "225 MATCHED"
ERROR = "400 ERROR"

#Global variables
PORT = 1337
loggedIn = False;
inGame = False;
clientSocket = None
justMatched = False
isChallenger = False

#TODO: Add select to be able to listen and send
#TODO: Still have to complete - PLAY

#TODO LATER: Block all action if they're not logged in?

def parseInput():
    #Reference globals
    global loggedIn
    global inGame
    global isChallenger
    global justMatched
    try:
        arguments = input().split()
        #If no arguments were  given, reprompt the user.
        if(len(arguments) == 0):
            return
        #If the help command is entered properly, print out the help message.
        elif(arguments[0] == "help" and len(arguments) == 1):
            print("login [String]: This command takes one argument, which is your name. This name will uniquely identify you to the "
                  "server. An example of how to use this command is to input 'login Michael'.\n\n"

                  "place [int]: This command takes one argument, which is an integer between 1 and 9 inclusive. This number identifies "
                  "the cell that you want to occupy with this move. An example of how to use this command is to input 'place 4'.\n\n"

                  "games: This command takes no arguments. It will trigger a query that is sent to the server, which will return a list of "
                  "current ongoing games. The game ID and the players are listed per game. You can only use this command when you are "
                  "not currently in a game.""\n\n"

                  "who: This command takes no arguments. It will trigger a query that is sent to the server, which will return a list of "
                  "players that are curently logged-in and available to play. You can only use this command when you are not currently in a game.\n\n"

                  "play [String]: This command takes on argument, which is the name of the player you would like to play a game with. If the "
                  "player is available, a game will be started between you and the other player. Otherwise, the server will tell you that a game "
                  "could not be started. At that point, you are free to choose another player to play against. You can only use this command when "
                  "you are not currently in a game.\n\n"

                  "exit: This command takes no arguments. Upon issuing this command, you will exit the server.The only way to use this "
                  "command is to input 'exit'.")
            return
        #If the login command is entered properly
        elif(arguments[0] == "login" and len(arguments) == 2):
            if(loggedIn):
                print("You are already logged in.")
                return
            #Generate the login message and send it to the server.
            loginMessage = LOGIN + " " + arguments[1]
            clientSocket.send(loginMessage.encode())
            #Grab server response and decode it
            response = clientSocket.recv(1024).decode()
            #If login was successful
            if(response == OK):
                #Note that the login was accepted
                loggedIn = True
                print("Login successful.")
                return
            #If login was not successful
            if(response == ERROR):
                #If client login attempt was denied by server, print out error message and reprompt.
                print("Login attempt was denied. Please select a different username.")
                return
        #If the place command is entered properly
        elif(arguments[0] == "place" and len(arguments) == 2):
            if(loggedIn == False):
                print("You cannot place a piece yet. You are not logged in and you are not in a game.")
                return
            if(inGame == False):
                print("You cannot place a piece yet. You are not in a game.")
                return
            #Try to obtain integer object using the second argument
            try:
                tileNumber = int(arguments[1])
            #If the second argument is unable to be converted to an integer object
            except ValueError:
                print("Error: The second argument must be an integer between 1 and 9 inclusive.")
                return
            #Make sure tileNumber is 1 to 9 inclusive
            if(tileNumber < 1 or tileNumber > 9):
                print("Error: The second argument must be an integer between 1 and 9 inclusive.")
                return
            #Generate place message
            placeMessage = PLACE + " " + arguments[1]
            #Send place message to server
            clientSocket.send(placeMessage.encode())
            #Receive the response from the server
            response = clientSocket.recv(1024).decode()
            #If move denied
            if(response == ERROR):
                #Inform the user that the move was invalid
                print("Invalid move. Spot on the board is already taken. Make another move.")
                return
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
                        print("Your opponent left the game. Sorry about that.")
                        print("You are being sent back to the lobby. Feel free to find another match or wait until someone else challenges you.")
                        justMatched = False
                        inGame = False
                        isChallenger = False
                        return
                    #Otherwise
                    else:
                        #Display board state
                        print(board[2])
                        #Wait for next message from the server
                        response = clientSocket.recv(1024).decode()
                        #If game is over and I won
                        if(response == WON):
                            print("The game is over. You won! Congratulations!")
                            justMatched = False
                            isChallenger = False
                            return
                        #If game is over and I lost
                        elif(response == LOST):
                            print("The game is over. You lost. Better luck next time!")
                            justMatched = False
                            isChallenger = False
                            return
                        #If game is over and I tied
                        elif(response == TIED) :
                            print("The game ended in a tie.")
                            justMatched = False
                            isChallenger = False
                            return
                        #If my turn
                        elif(response == GO):
                            print("It is your turn make your move.")
                            return
                else:
                    #If game is over and I won
                    if(response == WON):
                        print("The game is over. You won! Congratulations!")
                        justMatched = False
                        isChallenger = False
                        return
                    #If game is over and I lost
                    elif(response == LOST):
                        print("The game is over. You lost. Better luck next time!")
                        justMatched = False
                        isChallenger = False
                        return
                    #If game is over and I tied
                    elif(response == TIED) :
                        print("The game ended in a tie.")
                        justMatched = False
                        isChallenger = False
                        return
        #If the who command is entered properly
        elif(arguments[0] == "who" and len(arguments) == 1):
            #Check if in-game
            if(inGame):
                print("You cannot use this command while in a game.")
                return
            #Generate the who message and send it to the server
            whoMessage = WHO
            clientSocket.send(whoMessage.encode())
            #Grab server response and decode it
            response = clientSocket.recv(1024).decode()
            names = response.split()
            token = names[0] + " " + names[1]
            #If request was successful
            if(token == OK):
                if(len(names) == 2):
                    print("No players are ready to play at the moment.")
                    return
                else:
                    for index in range(2, len(names)):
                        print("Player ID: " + names[index])
                    return
            else:
                print("Error: Unable to fulfill request.")
                return
        #If the games command is entered properly
        elif(arguments[0] == "games" and len(arguments) == 1):
            #Check if in-game
            if(inGame):
                print("You cannot use this command while in a game.")
                return
            #Generate the games message
            gamesMessage = GAMES
            #Send games message to server
            clientSocket.send(gamesMessage.encode())
            #Wait for server response and decode it
            response = clientSocket.recv(1024).decode()
            #Split the response by spaces
            games = response.split()
            token = games[0] + " " + games[1]
            if(token == OK):
                if(len(games) == 2):
                    print("No ongoing games exist.")
                    return
                else:
                    for index in range(2, len(games)):
                        tokenized = games[index].split(',')
                        print("Game ID: " + tokenized[0])
                        print("Player ID: " + tokenized[1])
                        print("Player ID: " + tokenized[2])
                    return
            else:
                print("Error: Unable to fulfill request.")
                return
        #If the play command is entered properly
        elif(arguments[0] == "play" and len(arguments) == 2):

            #Check if in-game
            if(inGame):
                print("You cannot use this command while in a game.")
                return
            #Generate the play message
            playMessage = PLAY + " " + arguments[1]
            #Send play message to server
            clientSocket.send(playMessage.encode())
            #Wait for server response and decode it
            response = clientSocket.recv(1024).decode()
            #If request denied
            if(response == ERROR):
                print("Invalid play request.")
                return
            elif(response == OK):
                print("Play request accepted.")
                isChallenger = True
                inGame = True
                return
        #If the exit command is entered properly
        elif(arguments[0] == "exit" and len(arguments) == 1):
            #Generate the exit message
            exitMessage = EXIT
            #Send exit message to server
            clientSocket.send(exitMessage.encode())
            #Wait for server response and decode it.
            response = clientSocket.recv(1024).decode()
            #If the server acknowledged the exit message, print out the appropriate message and close the socket.
            if(response == OK):
                print("Exiting now. See you next time!")
                clientSocket.close()
                return EXIT
            else:
                print("Could not exit.")
        #If the given command does not match any of the supported commands, print out the error message and reprompt
        else:
            print("Error: Command not recognized. If you are not familiar with the accepted commands, feel free to input 'help' to see "
                  "the available commands, their uses, and how to use them.")
    #Catches ConnectionResetError
    except ConnectionResetError:
        print("Server has gone down.")
        print("Client closing.")
        return

def parseMessage():
    #Reference globals
    global inGame
    global justMatched
    global isChallenger
    #Wait for server response and decode it.
    response = clientSocket.recv(1024).decode()
    if(not isChallenger):
        if(response == MATCHED):
            print("You have been matched.")
            inGame = True
            justMatched = True
            clientSocket.send(OK.encode())
            return
        if(response == OK and justMatched):
            justMatched = False
            return
    if(response == START):
        print("Game is starting.")
        return
    if(response == WAIT and isChallenger):
        print("Wait for game to begin.")
        return
    if(response == WAIT and not isChallenger):
        print("Wait for opponent to make a move.")
        return
    else:
        isChallenger = False
    if(response == OK):
        print("Make a move.")
        return
    tokenized = response.split()
    token = tokenized[0] + " " + tokenized[1]
    if(token == NAME):
        print("Your opponent's login ID is: " + tokenized[2])
        return
    if(token == DISPLAY):
        tokenized = response.split(' ', 2)
        print(tokenized[2])
        return
    if(response == GO):
        print("Make a move.")
        return
    if(response == LEFT):
        print("Your opponent left the game. Sorry about that. You are now back in the lobby.")


#Main function that initiates the client
def main():
    global clientSocket
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
    #Set up clientSelectors to notify clientSocket when reading/writing is to be done
    clientSelectors = selectors.DefaultSelector()
    clientSelectors.register(clientSocket, selectors.EVENT_READ, parseMessage)
    clientSelectors.register(sys.stdin, selectors.EVENT_READ, parseInput)
    #Loop that runs the client until exit.
    while(True):
        events = clientSelectors.select()
        for key, mask in events:
            callback = key.data
            returnVal = callback()
            if returnVal == EXIT:
                return


#Calls the main function on execution
if __name__ == "__main__":
    main()

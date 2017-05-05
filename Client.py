#Michael Cheung
#Jake Tusa
#Billy Ko

#This is the client code.

#Imports
import sys
from socket import *

#Global variables
PORT = 1337
HOST = ""
#Main function that initiates the client
def main():
    #Checks that number of arguments is exactly 3
    if(len(sys.argv) != 3):
        print(
            "Error: There must be exactly 2 arguments to Client.py. The first argument must be the name of "
            "the machine on which the server program is running. The second argument must be the port number "
            "that the server is listening at."
        )
        return
    #Can't check the validity of the first argument here. If it is invalid, it will become apparent when trying to connect.
    HOST = sys.argv[1]
    #Try to obtain integer object using the second argument
    try:
        portNumber = int(sys.argv[2])
    #If the second argument is unable to be converted to an integer object
    except ValueError:
        print(
            "The second argument must be the port number that the server is listening at. A port number is an int."
        )
        return
    #Checks if the given port number matches the required port number
    if(portNumber != PORT):
        print(
            "Error: The second argument must be the number '1337'. This is the designated port that the server is listening at."
        )
        return
    #Create an INET, STREAMing socket
    clientSocket = socket(AF_INET, SOCK_STREAM)
    '''
    #Try to bind socket to the given host and port
    try:
        clientSocket.connect((HOST, PORT))
    except ConnectionRefusedError:
        print(
            "The connection to the server specified was refused. Your first argument seems to have been invalid."
        )
        return
    '''
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
            print(
                "help: This command takes no arguments. It prints out all commands available, a brief descriptions "
                "of each of them, and the syntax of their usage. The only way to use this command is to input 'help'.\n\n"

                "login [string]: This command takes one argument, which is your name. This name will uniquely identify you to the "
                "server. An example of how to use this command is to input 'login Michael'.\n\n"

                "place [int]: This command takes one argument, which is an integer between 1 and 9 inclusive. This number identifies "
                "the cell that you want to occupy with this move. An example of how to use this command is to input 'place 4'.\n\n"

                "exit: This command takes no arguments. Upon issuing this command, you will exit the server. You may issue this command "
                "whenever you want. The only way to use this command is to input 'exit'."
            )
        #If login command given
        elif(arguments[0] == "login" and len(arguments) == 2):
            #Generate login message
            loginMessage = "login: " + arguments[1]
            #Send login message to server
            #clientSocket.send(loginMessagee.encode())
            #Debug print out
            print(
                "Login message sent to server.\n"
                "Login message was: '" + loginMessage + "'"
            )
            '''
            #Receive the response from the server
            response = clientSocket.recv(1024)
            #Debug print out
            print(
                "Response from server: " + response.
            )
            #TODO: Add appropriate handling based on the code returned by the server
            '''
        #If place command given
        elif(arguments[0] == "place" and len(arguments) == 2):
            #Try to obtain integer object using the second argument
            try:
                tileNumber = int(arguments[1])
            #If the second argument is unable to be converted to an integer object
            except ValueError:
                print(
                    "Error: The second argument must be an integer between 1 and 9 inclusive."
                )
                continue
            #Make sure tileNumber is 1 to 9 inclusive
            if(tileNumber < 1 or tileNumber > 9):
                print(
                    "Error: The second argument must be an integer between 1 and 9 inclusive."
                )
                continue
            #Generate place message
            placeMessage = "place: " + arguments[1]
            #Send place message to server
            #clientSocket.send(placeMessage.encode())
            #Debug print out
            print(
                "Place message sent to server.\n"
                "Place message was: '" + placeMessage + "'"
            )
            '''
            #Receive the response from the server
            response = clientSocket.recv(1024)
            #Debug print out
            print(
                "Response from server: " + response.
            )
            #TODO: Add appropriate handling based on the code returned by the server
            '''
        #If exit command given
        elif(arguments[0] == "exit" and len(arguments) == 1):
            #Generate exit message
            exitMessage = "exiting"
            #Send exit message to server
            #clientSocket.send(exitMessage.encode())
            #Debug print out
            print(
                "Exit message sent to server.\n"
                "Exit message was: '" + exitMessage + "'"
            )
            #Close the socket
            clientSocket.close()
            print(
                "Exiting. See you next time!"
            )
            return
        #If given command line argument does not match any of the expected commands
        else:
            print(
                "Error: Command not recognized. If you are not familiar with the accepted commands, feel free to input 'help' to see "
                "the available commands, their uses, and how to use them."
            )


#Calls the main function on execution
if __name__ == "__main__":
    main()

#Names: Jake Tusa, Michael Cheung, Billy Ko
#Date: 5/6/17
#Purpose: CSE 310 Final Project Server

from socket import *

class Server:

    # Define global variables
    SERVER_PORT = 1337

    # Main function
    def main(self):
        # Initialize the server port & socket
        serverPort = SERVER_PORT
        serverSocket = socket(AF_INET, SOCK_STREAM)

        # Bind the socket and make it listen to requests (at most 1 at a time)
        serverSocket.bind(('', serverPort))
        serverSocket.listen(1)

        # Define variables to store player & game information
        numPlayers = 0
        player1 = None
        player2 = None
        game = None

        # While the server is running, loop
        while True:

            # While we don't have enough players for a game, loop
            while numPlayers < 2:

                # Accept & store incoming connections & addresses
                connectionSocket, addr = serverSocket.accept()

                try:
                    # Store the name of the player that logged in, update his/her
                    # state, and increment our player counter
                    if player1 == None:
                        player1 = Player()
                        player1.setConn(connectionSocket)
                        player1.setAddr(addr)
                        player1.setName(connectionSocket.recv(1024))
                        player1.setState("available")

                    elif player2 == None:
                        player2 = Player()
                        player2.setConn(connectionSocket)
                        player2.setAddr(addr)
                        player2.setName(connectionSocket.recv(1024))
                        player2.setState("available")

                    else:
                        raise ValueError("ValueError")

                except ValueError:
                        connectionSocket.send("HTTP/1.1 400 ERROR\r\n\r\n")
                        connectionSocket.send("This game already has two players -- please wait for the next game.")
                        connectionSocket.close()

                # Send a 200 OK message & increment the number of players
                connectionSocket.sendto("HTTP/1.1 200 OK\r\n\r\n", addr)
                numPlayers += 1

                # If we only have one player, tell him/her to wait
                if numPlayers == 1:
                    connectionSocket.sendto("Please wait a moment for another player to join", addr)

                # If we have two players, create a game and update the
                # players' states to be "busy"
                elif numPlayers == 2:
                    game = Game(connectionSocket)

                    # Update player states to reflect that they are in a game
                    player1.setState("busy")
                    player2.setState("busy")

                    # X always goes first in Tic Tac Toe
                    player1.setPiece("X")
                    player2.setPiece("O")

                    # Send playerIds to opposing players
                    connectionSocket.sendto("Opponent name: " + player2.getName(), player1.getAddr())
                    connectionSocket.sendto("Opponent name: " + player1.getName(), player2.getAddr())

                    # Set the game as active
                    game.setIsActive(True)

            # While there is a game active, loop
            while game.getIsActive() == True:

                # handle receiving of messages

        serverSocket.close()

class Player:

    # Player fields
    conn = None
    addr = None
    name = ""
    state = ""
    piece = ""

    # Accessor methods
    def getConn():
        return self.conn

    def getAddr():
        return self.addr

    def getName():
        return self.name

    def getState():
        return self.state

    def getPiece():
        return self.piece

    # Mutator methods
    def setConn(conn):
        self.conn = conn

    def setAddr(addr):
        self.addr = addr

    def setName(name):
        self.name = name

    def setState(state):
        self.state = state

    def setPiece(piece):
        self.piece = piece

class Game:

    # Static fields
    NUM_PLACES = 9
    BLANK = "."
    TIE = "TIE"

    # Regular fields
    board = None
    connectionSocket = None
    isActive = False

    def __init__(self, connectionSocket) {
        board = createBoard()
        self.connectionSocket = connectionSocket
    }

    # Accessor methods
    def getConnectionSocket():
        return self.connectionSocket

    def getIsActive():
        return self.isActive

    # Mutator methods
    def setIsActive(isActive):
        self.isActive = isActive

    def setConnectionSocket(connectionSocket):
        self.connectionSocket = connectionSocket

    # Function to initialize the list that holds the game board representation
    def createBoard():
        gameBoard = []
        for place in range(NUM_PLACES):
            gameBoard.append(BLANK)
        return gameBoard

    # Function to send a visualization of the current game board to the clients
    def sendBoard(gameBoard, player1, player2):
        display = """
        {0} {1} {2}
        {3} {4} {5}
        {6} {7} {8}""".format(gameBoard[0], gameBoard[1], gameBoard[2],
                              gameBoard[3], gameBoard[4], gameBoard[5],
                              gameBoard[6], gameBoard[7], gameBoard[8])

        # Send the formatted string to the clients
        connectionSocket.sendto(display, player1.getAddr())
        connectionSocket.sendto(display, player2.getAddr())

    # Function that checks the possible losing combinations
    # @return  Losing piece ("X" or "O"), "TIE" if tied, or None if not done yet
    def checkLoser(gameBoard):
        losingCombos = ((0, 1, 2), (0, 3, 6), (0, 4, 8),
                        (1, 4, 7), (2, 5, 8), (2, 4, 6),
                        (3, 4, 5), (6, 7, 8))

        for combo in losingCombos:
            if combo[0] == combo[1] == combo[2]:
                if combo[0] != BLANK:
                    return combo[0]

        if BLANK not in losingConvo:
            return TIE

        return None

# Create the server
server = Server()

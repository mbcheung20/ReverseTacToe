#Names: Jake Tusa, Michael Cheung, Billy Ko
#Date: 5/6/17
#Purpose: CSE 310 Final Project Server

import socketserver

class TCPHandler(socketserver.BaseRequestHandler):

    # Define global variables / protocols
    LOGIN = "210"
    PLACE = "211"
    EXIT = "212"
    WAIT = "213"
    START = "214"

    # Main function
    def handle(self):

        # Define variables to store player & game information
        numPlayers = 0
        nameList = []
        player1 = None
        player2 = None
        game = None

        # While the server is running, loop
        while True:

            # Accept incoming connections
            print("Connection accepted: " + self.client_address[0])
            self.request.send("200 OK".encode())

            # While we don't have enough players for a game, loop
            while numPlayers < 2:

                # Create temporary variables
                name = ""
                loginSuccess = False

                try:
                    # Handle incoming commands
                    message = self.request.recv(1024)
                    tokenized = message.split()

                    # Handle login requests
                    if tokenized[0] == LOGIN:
                        if message not in nameList:
                            nameList.append(message)
                            name = tokenized[1]
                            loginSuccess = True
                        else:
                            self.request.send("400 Error: Name already taken.".encode())

                    # Handle place requests
                    elif tokenized[0] == PLACE:
                        raise CommandError()

                    # Handle exit requests
                    elif tokenized[0] == EXIT:
                        self.request.send("212 Goodbye: Player has exited.".encode())

                    # Handle other requests
                    else:
                        raise BadCommandError()

                    # Store the name of the player that logged in, update his/her
                    # state, and increment our player counter
                    if player1 == None:
                        player1 = Player(self.request, addr, name, "available", "X")

                    elif player2 == None:
                        player2 = Player(self.request, addr, name, "available", "O")

                except CommandError():
                    self.request.send("400 Error: You cannot use that command at this time.".encode())

                except BadCommandError():
                    self.request.send("400 Error: Command not recognized.".encode())

                if loginSuccess:
                    # Increment the number of players
                    numPlayers += 1

                    # If we only have one player, tell him/her to wait
                    if numPlayers == 1:
                        self.request.send("Please wait a moment for another player to join.".encode())

                    # If we have two players, create a game and update the
                    # players' states to be "busy"
                    elif numPlayers == 2:
                        game = Game()

                        # Update player states to reflect that they are in a game
                        player1.setState("busy")
                        player2.setState("busy")

                        # Send playerIds to opposing players
                        oppPlayer1 = "Opponent name: " + player2.getName()
                        oppPlayer2 = "Opponent name: " + player1.getName()
                        player1.getConnectionSocket().send(oppPlayer1.encode())
                        player2.getConnectionSocket().send(oppPlayer2.encode())

                        # Set the game as active
                        game.setIsActive(True)

            # While there is a game active, loop
            while game.getIsActive() == True:

                turn = game.getCurrentTurn()

                try:
                    # Handle incoming commands
                    command = connectionSocket.recv(1024)
                    tokenized = command.split()

                    # Handle login requests
                    if (tokenized[0] == LOGIN):
                        raise CommandError()

                    # Handle place requests
                    elif (tokenized[0] == PLACE):
                        raise CommandError()

                    # Handle exit requests
                    elif (tokenized[0] == EXIT):
                        connectionSocket.send(EXIT + " Goodbye!".encode())
                        connectionSocket.close()

                    # Handle other requests
                    else:
                        raise BadCommandError()

                except CommandError():
                    connectionSocket.send("400 Error: You cannot use that command at this time.".encode())

class Player:

    # Player fields
    connectionSocket = None
    addr = None
    name = ""
    state = ""
    piece = ""

    def __init__(self, connectionSocket, addr, name, state, piece):
        self.connectionSocket = connectionSocket
        self.addr = addr
        self.name = name
        self.state = state
        self.piece = piece

    # Accessor methods
    def getConnectionSocket():
        return self.connectionSocket

    def getAddr():
        return self.addr

    def getName():
        return self.name

    def getState():
        return self.state

    def getPiece():
        return self.piece

    # Mutator methods
    def setConnectionSocket(connectionSocket):
        self.connectionSocket = connectionSocket

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
    gameBoard = None
    isActive = False

    def __init__(self):
        gameBoard = createBoard()

    # Accessor methods
    def getIsActive():
        return self.isActive

    # Mutator methods
    def setIsActive(isActive):
        self.isActive = isActive

    # Internal function to initialize the list that holds the game board representation
    def createBoard(self):
        tempBoard = []
        for eachPlace in range(NUM_PLACES):
            tempBoard.append(BLANK)
        return tempBoard

    # Function to send a visualization of the current game board to the clients
    def sendBoard(self, player1, player2):
        display = """
        {0} {1} {2}
        {3} {4} {5}
        {6} {7} {8}""".format(self.gameBoard[0], self.gameBoard[1], self.gameBoard[2],
                              self.gameBoard[3], self.gameBoard[4], self.gameBoard[5],
                              self.gameBoard[6], self.gameBoard[7], self.gameBoard[8])

        # Send the formatted string to the clients
        player1.getConnectionSocket.send(display.encode())
        player2.getConnectionSocket.send(display.encode())

    # Function that checks the possible losing combinations
    # @return  Losing piece ("X" or "O"), "TIE" if tied, or None if not done yet
    def checkLoser(self):
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

# New exceptions for invalid/bad commands
class CommandError(Exception):
    pass

class BadCommandError(Exception):
    pass

# Create the server
if __name__ == "__main__":
    SERVER_HOST = "localhost"
    SERVER_PORT = 1337
    server = socketserver.TCPServer((SERVER_HOST, SERVER_PORT), TCPHandler)
    server.serve_forever()

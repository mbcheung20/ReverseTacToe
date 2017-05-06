#Names: Jake Tusa, Michael Cheung, Billy Ko
#Date: 5/6/17
#Purpose: CSE 310 Final Project Server

import socketserver
import threading

# Define protocols
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

# Define global variables
playerList = []
nameList = []
playerWaiting = True
game = None

class ThreadedTCPHandler(socketserver.BaseRequestHandler):

    # Main function
    def handle(self):

        # Reference global protocols
        global LOGIN
        global PLACE
        global EXIT
        global WAIT
        global START
        global READY
        global WON
        global LOST
        global TIED
        global NAME
        global LEFT
        global DISPLAY

        # Reference the global variables that need to be shared
        global nameList
        global playerList
        global playerWaiting
        global game

        # Accept incoming connections
        print("Connection accepted: " + self.client_address[0])
        self.request.send("200 OK".encode())

        # If we don't have two players, attempt to add them to the game
        if len(playerList) < 2:

            # Create temporary variables
            name = ""
            loginSuccess = False
            player = None

            while loginSuccess == False:

                try:
                    # Handle incoming commands
                    message = self.request.recv(1024)
                    message = message.decode()
                    tokenized = message.split()

                    # Handle login requests
                    if tokenized[0] == LOGIN:

                        if message not in nameList:
                            nameList.append(message)
                            name = tokenized[1]
                            loginSuccess = True
                            self.request.send("200 OK".encode())
                        else:
                            self.request.send("400 ERROR".encode())

                    # Handle place requests
                    elif tokenized[0] == PLACE:
                        self.request.send("400 ERROR".encode())

                    # Handle exit requests
                    elif tokenized[0] == EXIT:
                        self.request.send((EXIT + " EXIT").encode())

                    # Handle other requests
                    else:
                        self.request.send("400 ERROR".encode())

                except IndexError:
                    pass

            # Store the name of the player that logged in, update his/her
            # state, and increment our player counter
            if not playerList:
                player = Player(self.request, self.client_address, name, "available", "X", True)

            else:
                player = Player(self.request, self.client_address, name, "available", "O", False)

            playerList.append(player)

            # If we only have one player, tell him/her to wait
            if player.getPiece() == "X":
                self.request.send((WAIT + " WAIT").encode())
                while playerWaiting == True:
                    pass

            # Set up the game
            elif player.getPiece() == "O":
                game = Game()
                game.createBoard()
                for eachPlayer in playerList:
                    game.addPlayer(eachPlayer)
                playerWaiting = False

            # Update player state to reflect that they are in a game
            player.setState("busy")

            # Let the players know that the game is about to start
            self.request.send((START + " START").encode())

            # Send playerIds to opposing players
            for gamePlayer in game.getPlayerList():
                if gamePlayer != player:
                    opposingPlayer = NAME + " NAME: " + gamePlayer.getName()
                    self.request.send(opposingPlayer.encode())

            # Set the game as active
            game.setIsActive(True)

        # While there is a game active, loop
        while game.getIsActive() == True:

            # Update wait variable
            playerWaiting = True

            # Send the players the visualization of the board
            boardDisplay = game.displayBoard()
            self.request.send((DISPLAY + " DISPLAY: " + boardDisplay).encode())

            # Check which player's turn it is and message them accordingly
            turn = game.getCurrentTurn()
            if turn == player.getPiece():
                self.request.send((READY + " READY").encode())

                # Loop variable
                commandSuccess = False
                while not commandSuccess:

                    try:
                        # Handle incoming commands
                        command = self.request.recv(1024)
                        command = command.decode()
                        tokenized = command.split()

                        # Handle login requests
                        if (tokenized[0] == LOGIN):
                            self.request.send("400 ERROR".encode())

                        # Handle place requests
                        elif (tokenized[0] == PLACE):
                            raise CommandError()

                        # Handle exit requests
                        elif (tokenized[0] == EXIT):
                            self.request.send((EXIT + " EXIT").encode())        # DO WEIRD THINGS HERE

                        # Handle other requests
                        else:
                            self.request.send("400 ERROR".encode())

            else:
                self.request.send((WAIT + " WAIT").encode())
                while playerWaiting == True:
                    pass

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class Player:

    # Player fields
    connectionSocket = None
    addr = None
    name = ""
    state = ""
    piece = ""
    isTurn = False

    def __init__(self, connectionSocket, addr, name, state, piece, isTurn):
        self.connectionSocket = connectionSocket
        self.addr = addr
        self.name = name
        self.state = state
        self.piece = piece
        self.isTurn = isTurn

    # Accessor methods
    def getConnectionSocket(self):
        return self.connectionSocket

    def getAddr(self):
        return self.addr

    def getName(self):
        return self.name

    def getState(self):
        return self.state

    def getPiece(self):
        return self.piece

    def getIsTurn(self):
        return self.isTurn

    # Mutator methods
    def setConnectionSocket(self, connectionSocket):
        self.connectionSocket = connectionSocket

    def setAddr(self, addr):
        self.addr = addr

    def setName(self, name):
        self.name = name

    def setState(self, state):
        self.state = state

    def setPiece(self, piece):
        self.piece = piece

    def setIsTurn(self, isTurn):
        self.isTurn = isTurn

class Game:

    # Static fields
    NUM_PLACES = 9
    BLANK = "."
    TIE = "TIE"

    # Regular fields
    playerList = []
    gameBoard = []
    isActive = False

    #def __init__(self):
        #gameBoard = createBoard(self)

    # Accessor methods
    def getPlayerList(self):
        return self.playerList

    def getIsActive(self):
        return self.isActive

    # Mutator methods
    def setIsActive(self, isActive):
        self.isActive = isActive

    def addPlayer(self, player):
        self.playerList.append(player)

    # Internal function to initialize the list that holds the game board representation
    def createBoard(self):
        tempBoard = []
        for eachPlace in range(self.NUM_PLACES):
            tempBoard.append(self.BLANK)
        self.gameBoard = tempBoard

    # Function to send a visualization of the current game board to the clients
    def displayBoard(self, player1, player2):
        display = """
        {0} {1} {2}
        {3} {4} {5}
        {6} {7} {8}""".format(self.gameBoard[0], self.gameBoard[1], self.gameBoard[2],
                              self.gameBoard[3], self.gameBoard[4], self.gameBoard[5],
                              self.gameBoard[6], self.gameBoard[7], self.gameBoard[8])

        return display

    # Function to check whose turn it is to move
    def getCurrentTurn(self):
        for eachPlayer in self.playerList:
            if eachPlayer.getIsTurn() == True:
                return eachPlayer.getPiece()

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

# Create the server
if __name__ == "__main__":
    SERVER_HOST = "localhost"
    SERVER_PORT = 1337
    server = ThreadedTCPServer((SERVER_HOST, SERVER_PORT), ThreadedTCPHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

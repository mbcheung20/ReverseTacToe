#Names: Jake Tusa, Michael Cheung, Billy Ko
#Date: 5/7/17
#Purpose: CSE 310 Final Project Server

#This code satisfies part 1.

# Imports
import socketserver
import threading
from time import sleep

# Protocols
OK = "200 OK"
LOGIN = "210"
PLACE = "211"
EXIT = "212"
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
ERROR = "400 ERROR"

# Global variables
playerList = []
nameList = []
gameList = []
playerWaiting = True
playerExited = False
game = None

class ThreadedTCPHandler(socketserver.BaseRequestHandler):

    # Main function
    def handle(self):

        # Reference the global variables that need to be shared
        global nameList
        global playerList
        global gameList
        global playerExited
        global playerWaiting
        global game

        # Create a variable that allows us to reach the end of the control flow
        killThread = False

        # Accept incoming connections
        print("Connection accepted: " + self.client_address[0])
        sleep(0.1)
        self.request.send(OK.encode())

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

                        if tokenized[1] not in nameList:
                            nameList.append(tokenized[1])
                            name = tokenized[1]
                            loginSuccess = True
                            sleep(0.1)
                            self.request.send(OK.encode())
                        else:
                            sleep(0.1)
                            self.request.send(ERROR.encode())

                    # Handle place requests
                    elif tokenized[0] == PLACE:
                        sleep(0.1)
                        self.request.send(ERROR.encode())

                    # Handle exit requests
                    elif tokenized[0] == EXIT:
                        sleep(0.1)
                        self.request.send(OK.encode())
                        killThread = True
                        break

                    # Handle other requests
                    else:
                        sleep(0.1)
                        self.request.send(ERROR.encode())

                except IndexError:
                    pass

            # Exit the function
            if killThread == True:
                return

            # Store the name of the player that logged in, update his/her
            # state, and increment our player counter
            if not playerList:
                player = Player(name, "available", "X", True)

            else:
                player = Player(name, "available", "O", False)

            playerList.append(player)

            # If we only have one player, tell him/her to wait
            if player.getPiece() == "X":
                sleep(0.1)
                self.request.send(WAIT.encode())
                while playerWaiting == True:
                    pass

            # Set up the game
            elif player.getPiece() == "O":
                if game == None:
                    game = Game()
                game.createBoard()
                for eachPlayer in playerList:
                    if eachPlayer not in game.getPlayerList():
                        game.addPlayer(eachPlayer)
                playerWaiting = False

            # Update player state to reflect that they are in a game
            player.setState("busy")

            # Let the players know that the game is about to start
            sleep(0.1)
            self.request.send(START.encode())

            # Send playerIds to opposing players
            for gamePlayer in game.getPlayerList():
                if gamePlayer != player:
                    opposingPlayer = NAME + ": " + gamePlayer.getName()
                    sleep(0.1)
                    self.request.send(opposingPlayer.encode())

            # If this player is a replacement, stop the other player from looping
            playerExited = False

            # Set the game as active
            game.setIsActive(True)

        # While there is a game active, loop
        while game.getIsActive() == True:

            if killThread == True:
                break

            # If someone left the game, wait for a new player and then restart
            if playerExited == True:
                self.request.send(LEFT.encode())
                player.setPiece("X")
                player.setIsTurn(True)
                sleep(0.1)
                while playerExited == True:
                    pass
                sleep(0.1)
                self.request.send(START.encode())

                # Send name to new player
                for gamePlayer in game.getPlayerList():
                    if gamePlayer != player:
                        opposingPlayer = NAME + ": " + gamePlayer.getName()
                        sleep(0.2)
                        self.request.send(opposingPlayer.encode())

            # Send the players the visualization of the board
            boardDisplay = game.displayBoard()
            sleep(0.1)
            self.request.send((DISPLAY + " " + boardDisplay).encode())

            # Check to see if the game is over
            gameLoser = game.checkLoser()

            # If the game was a tie, notify the players and restart the game
            if gameLoser == "TIE":
                sleep(0.1)
                self.request.send(TIED.encode())
                game.createBoard()
                sleep(0.1)
                self.request.send(START.encode())
                newDisplay = game.displayBoard()
                sleep(0.1)
                self.request.send((DISPLAY + " " + newDisplay).encode())

            # If there is a winner, notify both players and restart the game
            elif gameLoser == "X" or gameLoser == "O":
                playerPiece = player.getPiece()

                # Update turns for the next game
                if playerPiece == "X":
                    player.setIsTurn(True)
                else:
                    player.setIsTurn(False)

                # Send a won or lost message to the players
                if gameLoser == playerPiece:
                    sleep(0.1)
                    self.request.send(LOST.encode())
                else:
                    sleep(0.1)
                    self.request.send(WON.encode())
                    game.createBoard()

                # Send the refreshed game board
                sleep(0.1)
                self.request.send(START.encode())
                newDisplay = game.displayBoard()
                sleep(0.1)
                self.request.send((DISPLAY + " " + newDisplay).encode())

            # Update wait variable
            playerWaiting = True

            # Check which player's turn it is and message them accordingly
            if player.getIsTurn() == True:
                sleep(0.1)
                self.request.send(GO.encode())

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
                            sleep(0.1)
                            self.request.send(ERROR.encode())

                        # Handle place requests
                        elif (tokenized[0] == PLACE):
                            attemptMove = game.updateBoard(player, tokenized[1])
                            if attemptMove == -1:
                                sleep(0.1)
                                self.request.send(ERROR.encode())
                            else:
                                sleep(0.1)
                                self.request.send(OK.encode())
                                player.setIsTurn(False)
                                commandSuccess = True
                                playerWaiting = False

                        # Handle exit requests
                        elif (tokenized[0] == EXIT):
                            self.request.send(OK.encode())
                            nameList.remove(player.getName())
                            playerList.remove(player)
                            game.removePlayer(player)
                            playerExited = True
                            playerWaiting = False
                            killThread = True
                            sleep(0.2)

                        # Handle other requests
                        else:
                            self.request.send(ERROR.encode())

                    except IndexError:
                        pass

            else:
                sleep(0.1)
                self.request.send(WAIT.encode())
                player.setIsTurn(True)
                while playerWaiting == True:
                    pass

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

#Represents a player
class Player:

    # Player fields
    name = ""
    state = ""
    piece = ""
    isTurn = False

    # Constructor
    def __init__(self, name, state, piece, isTurn):
        self.name = name
        self.state = state
        self.piece = piece
        self.isTurn = isTurn

    # Getters
    def getName(self):
        return self.name

    def getState(self):
        return self.state

    def getPiece(self):
        return self.piece

    def getIsTurn(self):
        return self.isTurn

    # Setters
    def setName(self, name):
        self.name = name

    def setState(self, state):
        self.state = state

    def setPiece(self, piece):
        self.piece = piece

    def setIsTurn(self, isTurn):
        self.isTurn = isTurn

#Represents a game of modified tic tac toe
class Game:

    # Static fields
    NUM_PLACES = 9
    BLANK = "."
    TIE = "TIE"

    # Regular fields
    gameID = 0
    playerList = []
    gameBoard = []
    isActive = False

    # Getters
    def getGameID(self):
        return self.gameID

    def getPlayerList(self):
        return self.playerList

    def getIsActive(self):
        return self.isActive

    # Setters
    def setGameID(self, gameID):
        self.gameID = gameID

    def setIsActive(self, isActive):
        self.isActive = isActive

    def addPlayer(self, player):
        self.playerList.append(player)

    def removePlayer(self, player):
        self.playerList.remove(player)

    # Initialize the list that holds the game board representation
    def createBoard(self):
        tempBoard = []
        for eachPlace in range(self.NUM_PLACES):
            tempBoard.append(self.BLANK)
        self.gameBoard = tempBoard

    # Returns a visualization of the current game board to send the clients
    # @return String representing the display, always successful
    def displayBoard(self):
        display = """
        {0} {1} {2}
        {3} {4} {5}
        {6} {7} {8}""".format(self.gameBoard[0], self.gameBoard[1], self.gameBoard[2],
                              self.gameBoard[3], self.gameBoard[4], self.gameBoard[5],
                              self.gameBoard[6], self.gameBoard[7], self.gameBoard[8])

        return display

    # Update the board with the player's piece placement
    # @return 0 on successful
    # @return -1 on failure
    def updateBoard(self, player, place):
        intPlace = int(place)
        if self.gameBoard[intPlace - 1] == self.BLANK:
            self.gameBoard[intPlace - 1] = player.getPiece()
            return 0
        else:
            return -1

    # Function that checks the possible losing combinations
    # @return  Losing piece ("X" or "O"), "TIE" if tied, or None if not done yet
    def checkLoser(self):
        losingCombos = ((0, 1, 2), (0, 3, 6), (0, 4, 8),
                        (1, 4, 7), (2, 5, 8), (2, 4, 6),
                        (3, 4, 5), (6, 7, 8))

        for combo in losingCombos:
            if self.gameBoard[combo[0]] == self.gameBoard[combo[1]] == self.gameBoard[combo[2]]:
                if self.gameBoard[combo[0]] != self.BLANK:
                    return self.gameBoard[combo[0]]

        if self.BLANK not in self.gameBoard:
            return self.TIE

        return None

# Create the server
if __name__ == "__main__":
    SERVER_HOST = "localhost"
    SERVER_PORT = 1337
    server = ThreadedTCPServer((SERVER_HOST, SERVER_PORT), ThreadedTCPHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()

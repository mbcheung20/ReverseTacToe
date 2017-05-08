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
WHO = "222"
GAMES = "223"
PLAY = "224"
MATCHED = "225 MATCHED"
ERROR = "400 ERROR"

# Global variables
playerList = []
localPlayerList = []
nameList = []
gameList = []
totalGames = 0
waitingOnGame = True

class ThreadedTCPHandler(socketserver.BaseRequestHandler):

    # Main function
    def handle(self):

        # Reference the global variables that need to be shared
        global playerList
        global localPlayerList
        global nameList
        global gameList
        global totalGames
        global waitingOnGame

        # Local variables to each thread/client
        localGameID = -1
        lobbyLoop = True
        exitLobbyLoop = True
        killThread = False

        # Accept incoming connections
        print("Connection from IP: " + self.client_address[0] + " accepted.")
        sleep(0.1)
        self.request.send(OK.encode())

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

                    if tokenized[2] not in nameList:
                        nameList.append(tokenized[2])
                        name = tokenized[2]
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

                # Handle who requests
                elif tokenized[0] == WHO:
                    whoString = OK + " "
                    for eachPlayer in playerList:
                        whoString = whoString + eachPlayer.getName() + " "
                    whoString = whoString.rstrip()
                    sleep(0.1)
                    self.request.send(whoString.encode())

                # Handle games requests
                elif tokenized[0] == GAMES:
                    gamesString = OK
                    for eachGame in gameList:
                        gamesString = gamesString + " " + str(eachGame.getGameID()) + ","
                        for eachPlayer in eachGame.getPlayerList():
                            gamesString = gamesString + eachPlayer.getName() + ","
                        gamesString = gamesString.rstrip(',')
                    sleep(0.1)
                    self.request.send(gamesString.encode())

                # Handle play requests
                elif tokenized[0] == PLAY:
                    sleep(0.1)
                    self.request.send(ERROR.encode())

                # Handle other requests
                else:
                    sleep(0.1)
                    self.request.send(ERROR.encode())

            except IndexError:
                return

            except ConnectionResetError:
                print("Client at IP: " + self.client_address[0] + " exited unceremoniously.")

        # Exit the function
        if killThread == True:
            return

        # Add the new player to the lobby list
        player = Player()
        player.setConnSocket(self.request)
        player.setName(name)
        player.setState("available")
        playerList.append(player)

        # Place the player in a lobby
        while lobbyLoop == True:

            try:
                # Handle incoming commands
                lobbyMessage = self.request.recv(1024)
                lobbyMessage = lobbyMessage.decode()
                tokenized = lobbyMessage.split()

                # Handle login requests
                if tokenized[0] == LOGIN:
                    sleep(0.1)
                    self.request.send(ERROR.encode())

                # Handle place requests
                elif tokenized[0] == PLACE:
                    sleep(0.1)
                    self.request.send(ERROR.encode())

                # Handle exit requests
                elif tokenized[0] == EXIT:
                    sleep(0.1)
                    nameList.remove(name)
                    self.request.send(OK.encode())
                    killThread = True
                    break

                # Handle who requests
                elif tokenized[0] == WHO:
                    whoString = OK + " "
                    for eachPlayer in playerList:
                        whoString = whoString + eachPlayer.getName() + " "
                    whoString = whoString.rstrip()
                    sleep(0.1)
                    self.request.send(whoString.encode())

                # Handle games requests
                elif tokenized[0] == GAMES:
                    gamesString = OK
                    for eachGame in gameList:
                        gamesString = gamesString + " " + str(eachGame.getGameID()) + ","
                        for eachPlayer in eachGame.getPlayerList():
                            gamesString = gamesString + eachPlayer.getName() + ","
                        gamesString = gamesString.rstrip(',')
                    sleep(0.1)
                    self.request.send(gamesString.encode())

                # Handle play requests
                elif tokenized[0] == PLAY:
                    oppName = tokenized[2]
                    foundOpposing = False
                    for eachPlayer in playerList:
                        if oppName == eachPlayer.getName() and oppName != player.getName():
                            localPlayerList.append(eachPlayer)
                            localPlayerList.append(player)
                            player.setPiece("X")
                            player.setIsTurn(True)
                            foundOpposing = True
                            lobbyLoop = False
                            sleep(0.1)
                            self.request.send(OK.encode())
                            oppSocket = eachPlayer.getConnSocket()
                            sleep(0.1)
                            oppSocket.send(MATCHED.encode())
                    if foundOpposing == False:
                        sleep(0.1)
                        self.request.send(ERROR.encode())

                elif tokenized[0] == "200":
                    player.setPiece("O")
                    player.setIsTurn(False)
                    lobbyLoop = False
                    sleep(0.1)
                    self.request.send(OK.encode())

                # Handle other requests
                else:
                    sleep(0.1)
                    self.request.send(ERROR.encode())

            except IndexError:
                return

            except ConnectionResetError:
                print("Client at IP: " + self.client_address[0] + " exited unceremoniously.")

        if killThread == True:
            return

        # If we only have one player, tell him/her to wait
        if player.getPiece() == "X":
            sleep(0.1)
            self.request.send(WAIT.encode())
            while waitingOnGame == True:
                pass

        # Set up the game
        elif player.getPiece() == "O":
            localGame = Game()
            totalGames += 1
            localGame.setGameID(totalGames)
            localGame.createBoard()
            print("got here")
            for eachPlayer in localPlayerList:
                print("Adding " + eachPlayer.getName() + " to local game " + str(localGame.getGameID()))                          ###
                localGame.addPlayer(eachPlayer)
            localPlayerList = []
            gameList.append(localGame)
            waitingOnGame = False
            sleep(0.1)

        # Get the local game's ID on both clients
        localGameID = gameList[totalGames-1].getGameID()

        # Update player state to reflect that they are in a game
        player.setState("busy")

        # Let the players know that the game is about to start
        sleep(0.1)
        self.request.send(START.encode())

        # Get a reference to our local game
        localGame = self.findGameByGameID(localGameID)

        # Send playerIds to opposing players
        for gamePlayer in localGame.getPlayerList():
            if gamePlayer != player:
                opposingPlayer = NAME + ": " + gamePlayer.getName()
                sleep(0.1)
                self.request.send(opposingPlayer.encode())

        # If this player is a replacement, stop the other player from looping
        localGame.setPlayerExited(False)

        # Set the game as active
        localGame.setIsActive(True)

        # Remove the players from the active players list
        playerList.remove(player)

        if killThread == True:
            return

        # While there is a game active, loop
        localGame = self.findGameByGameID(localGameID)
        while localGame.getIsActive() == True:

            if killThread == True:
                break

            # If someone left the game, send the other player back to the "lobby" and delete the game
            if localGame.getPlayerExited() == True:
                localGame.removePlayer(player)
                gameList.remove(localGame)
                playerList.append(player)
                self.request.send(LEFT.encode())
                sleep(0.1)
                # Place the player in a lobby
                while exitLobbyLoop == True:

                    try:
                        # Handle incoming commands
                        exitLobbyMessage = self.request.recv(1024)
                        exitLobbyMessage = exitLobbyMessage.decode()
                        tokenized = exitLobbyMessage.split()

                        # Handle login requests
                        if tokenized[0] == LOGIN:
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
                            return

                        # Handle who requests
                        elif tokenized[0] == WHO:
                            whoString = OK + " "
                            for eachPlayer in playerList:
                                whoString = whoString + eachPlayer.getName() + " "
                            whoString = whoString.rstrip()
                            sleep(0.1)
                            self.request.send(whoString.encode())

                        # Handle games requests
                        elif tokenized[0] == GAMES:
                            gamesString = OK
                            for eachGame in gameList:
                                gamesString = gamesString + " " + str(eachGame.getGameID()) + ","
                                for eachPlayer in eachGame.getPlayerList():
                                    gamesString = gamesString + eachPlayer.getName() + ","
                                gamesString = gamesString.rstrip(',')
                            sleep(0.1)
                            self.request.send(gamesString.encode())

                        # Handle play requests
                        elif tokenized[0] == PLAY:
                            oppName = tokenized[2]
                            foundOpposing = False
                            for eachPlayer in playerList:
                                if oppName == eachPlayer.getName() and oppName != player.getName():
                                    player.setPiece("X")
                                    player.setIsTurn(True)
                                    foundOpposing = True
                                    lobbyLoop = False
                                    sleep(0.1)
                                    self.request.send(OK.encode())
                                    oppSocket = eachPlayer.getConnSocket()
                                    sleep(0.1)
                                    oppSocket.send(MATCHED.encode())
                            if foundOpposing == False:
                                sleep(0.1)
                                self.request.send(ERROR.encode())

                        elif tokenized[0] == "200":
                            player.setPiece("O")
                            player.setIsTurn(False)
                            lobbyLoop = False
                            sleep(0.1)
                            self.request.send(OK.encode())

                        # Handle other requests
                        else:
                            sleep(0.1)
                            self.request.send(ERROR.encode())

                    except IndexError:
                        return

                    except ConnectionResetError:
                        print("Client at IP: " + self.client_address[0] + " exited unceremoniously.")

                # If we only have one player, tell him/her to wait
                if player.getPiece() == "X":
                    sleep(0.1)
                    self.request.send(WAIT.encode())
                    while waitingOnGame == True:
                        pass

                # Set up the game
                elif player.getPiece() == "O":
                    localGame = Game()
                    totalGames += 1
                    localGame.setGameID(totalGames)
                    localGame.createBoard()
                    for eachPlayer in playerList:
                        if eachPlayer not in localGame.getPlayerList():
                            localGame.addPlayer(eachPlayer)
                    gameList.append(localGame)
                    waitingOnGame = False
                    sleep(0.1)

                # Get the local game's ID on both clients
                localGameID = gameList[totalGames-1].getGameID()

                # Update player state to reflect that they are in a game
                player.setState("busy")

                # Let the players know that the game is about to start
                sleep(0.1)
                self.request.send(START.encode())

                # Get a reference to our local game
                localGame = self.findGameByGameID(localGameID)

                # Send playerIds to opposing players
                for gamePlayer in localGame.getPlayerList():
                    if gamePlayer != player:
                        opposingPlayer = NAME + ": " + gamePlayer.getName()
                        sleep(0.1)
                        self.request.send(opposingPlayer.encode())

                # If this player is a replacement, stop the other player from looping
                localGame.setPlayerExited(False)

                # Set the game as active
                localGame.setIsActive(True)

                # Remove the players from the active players list
                playerList.remove(player)

                # Tell player that the game is starting
                self.request.send(START.encode())

            # Send the players the visualization of the board
            boardDisplay = localGame.displayBoard()
            sleep(0.1)
            self.request.send((DISPLAY + " " + boardDisplay).encode())

            # Check to see if the game is over
            gameLoser = localGame.checkLoser()

            # If the game was a tie, notify the players and restart the game
            if gameLoser == "TIE":
                sleep(0.1)
                self.request.send(TIED.encode())
                localGame.createBoard()
                sleep(0.1)
                self.request.send(START.encode())
                newDisplay = localGame.displayBoard()
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
                    localGame.createBoard()

                # Send the refreshed game board
                sleep(0.1)
                self.request.send(START.encode())
                newDisplay = localGame.displayBoard()
                sleep(0.1)
                self.request.send((DISPLAY + " " + newDisplay).encode())

            # Update wait variable
            localGame.setPlayerWaiting(True)

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
                            attemptMove = localGame.updateBoard(player, tokenized[2])
                            if attemptMove == -1:
                                sleep(0.1)
                                self.request.send(ERROR.encode())
                            else:
                                sleep(0.1)
                                self.request.send(OK.encode())
                                player.setIsTurn(False)
                                commandSuccess = True
                                localGame.setPlayerWaiting(False)

                        # Handle exit requests
                        elif (tokenized[0] == EXIT):
                            self.request.send(OK.encode())
                            nameList.remove(player.getName())
                            localGame.removePlayer(player)
                            localGame.setPlayerExited(True)
                            localGame.setPlayerWaiting(False)
                            killThread = True
                            sleep(0.2)

                        # Handle who requests
                        elif tokenized[0] == WHO:
                            whoString = OK + " "
                            for eachPlayer in playerList:
                                whoString = whoString + eachPlayer.getName() + " "
                            whoString = whoString.rstrip()
                            sleep(0.1)
                            self.request.send(whoString.encode())

                        # Handle games requests
                        elif tokenized[0] == GAMES:
                            gamesString = OK
                            for eachGame in gameList:
                                gamesString = gamesString + " " + str(eachGame.getGameID()) + ","
                                for eachPlayer in eachGame.getPlayerList():
                                    gamesString = gamesString + eachPlayer.getName() + ","
                                gamesString = gamesString.rstrip(',')
                            sleep(0.1)
                            self.request.send(gamesString.encode())

                        # Handle play requests
                        elif tokenized[0] == PLAY:
                            sleep(0.1)
                            self.request.send(ERROR.encode())

                        # Handle other requests
                        else:
                            self.request.send(ERROR.encode())

                    except IndexError:
                        return

                    except ConnectionResetError:
                        print("Client at IP: " + self.client_address[0] + " exited unceremoniously.")

            else:
                sleep(0.1)
                self.request.send(WAIT.encode())
                player.setIsTurn(True)
                while localGame.getPlayerWaiting() == True:
                    pass

    # Find an active game by its gameID
    def findGameByGameID(self, gameID):
        for eachGame in gameList:
            if eachGame.getGameID() == gameID:
                return eachGame
        return None

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

#Represents a player
class Player:

    # Player fields
    connSocket = None
    name = ""
    state = ""
    piece = ""
    isTurn = False

    # Constructor
    '''
    def __init__(self, connSocket, name, state, piece, isTurn):
        self.connSocket = connSocket
        self.name = name
        self.state = state
        self.piece = piece
        self.isTurn = isTurn
        '''

    # Getters
    def getConnSocket(self):
        return self.connSocket

    def getName(self):
        return self.name

    def getState(self):
        return self.state

    def getPiece(self):
        return self.piece

    def getIsTurn(self):
        return self.isTurn

    # Setters
    def setConnSocket(self, connSocket):
        self.connSocket = connSocket

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
    gameID = -1
    playerList = []
    gameBoard = []
    isActive = False
    playerWaiting = True
    playerExited = False

    # Getters
    def getGameID(self):
        return self.gameID

    def getPlayerList(self):
        return self.playerList

    def getIsActive(self):
        return self.isActive

    def getPlayerWaiting(self):
        return self.playerWaiting

    def getPlayerExited(self):
        return self.playerExited

    # Setters
    def setGameID(self, gameID):
        self.gameID = gameID

    def setIsActive(self, isActive):
        self.isActive = isActive

    def setPlayerWaiting(self, playerWaiting):
        self.playerWaiting = playerWaiting

    def setPlayerExited(self, playerExited):
        self.playerExited = playerExited

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

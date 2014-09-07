from Tkinter import *
import tkSimpleDialog
import tkMessageBox
import random
import copy

class Game():

###############################################
#INNER CLASSES
###############################################
    class Player(object):

        def __init__(self, game, name="Player"):
            
            #player has a name, score, hand, and access to game variables
            self.name = name
            self.score = 0
            self.game = game
            self.hand = self.game.bag.draw(7)
            self.status = "active"

        def __repr__(self):
            #prints out the player's hand incl. letter values
            result = ''
            letters = []
            for i in range(len(self.hand)):
                letter = self.hand[i].lower().strip()
                result += letter + ' '
                letters.append(letter)
            result += '\n'
            for i in range(len(self.hand)):
                result += str(self.game.WORD_VALUES[letters[i]]) + ' '

            return result

        def reload(self):
            # reloads letters in hand (if there are enough left in the bad)
            if (7 - len(self.hand) > len(self.game.bag.contents)):
                newLetters = self.game.bag.draw(len(self.game.bag.contents))
            else:
                newLetters = self.game.bag.draw(7 - len(self.hand)) 
            for letter in newLetters:
                self.hand.append(letter)
            pass

        def swap(self):
            # swaps all letters in hand
            if (len(self.hand) < 7):
                print "There aren't any letters to swap."
                return 'invalid'
            else:
                for i in range(len(self.hand)):
                    tile = self.hand.pop(6-i)
                    self.game.bag.add(tile)
                self.reload()

        def quit(self):
            #removes letter values of hand from score
            for letter in self.hand:
                self.score -= self.game.WORD_VALUES[letter]
            self.status = "forfeited"

        def isActive(self):
            return (self.status == "active")


    class LetterBag(object):

        def __init__(self):
            self.contents = []
            self.contents.append('q')
            self.contents.append('z')
            self.contents.append('j')
            self.contents.append('x')
            self.contents.append('k')
            for i in range(0, 2): #normally 2
                self.contents.append('f')
                self.contents.append('h')
                self.contents.append('v')
                self.contents.append('w')
                self.contents.append('y')
                self.contents.append('b')
                self.contents.append('c')
                self.contents.append('m')
                self.contents.append('p')
                self.contents.append('[]')
            for i in range(0, 3): # normally 3
                self.contents.append('g')
            for i in range(0, 12): # normally 12
                self.contents.append('e')
                if i < 4:
                    self.contents.append('d')
                    self.contents.append('u')
                    self.contents.append('s')
                    self.contents.append('l')
                if i < 6:
                    self.contents.append('t')
                    self.contents.append('r')
                    self.contents.append('n')
                if i < 8:
                    self.contents.append('o')
                if i < 9:
                    self.contents.append('i')
                    self.contents.append('a')

        # draws letters from bag, removing them from its contents
        def draw(self, numTiles):
            numDrawn = 0
            tilesDrawn = []
            for i in range(0, numTiles):
                selection = random.randint(0, len(self.contents) - 1)
                tileDrawn = self.contents.pop(selection)
                tilesDrawn.append(tileDrawn)
            return tilesDrawn

        #adds a tile back to the bag. 
        def add(self, tile):
            self.contents.append(tile)


    def __init__(self,master):


        self.WORD_VALUES = {'a': 1, 'b': 3, 'c': 3, 'd': 2, 'e': 1, 'f': 4,
                            'g': 2, 'h': 4, 'i': 1, 'j': 8, 'k': 5, 'l': 1,
                            'm': 3, 'n': 1, 'o': 1, 'p': 3, 'q': 10, 'r': 1,
                            's': 1, 't': 1, 'u': 1, 'v': 4, 'w': 4, 'x': 8,
                            'y': 4, 'z': 10, '[]': 0}
        BIG_FILE = open("sowpods.txt")
        self.VALID_WORDS = []
        for line in BIG_FILE:
            self.VALID_WORDS.append(line.strip())



        self.canvas = Canvas(master, width=450, height=500)
        self.canvas.grid(row=0, column=0)

        self.frame = Frame(master, bd=5, relief=GROOVE, height=500, width=500)
        self.frame.grid(row=0,column=1)

        self.createGame()
        self.createBoard()

        self.buildFrame()

        self._drag_data = {"item": None, "x": 0, "y": 0, "xStart": 0, "yStart": 0}


        self.canvas.tag_bind("hand", "<ButtonPress-1>", self.OnLetterButtonPress)
        self.canvas.tag_bind("hand", "<ButtonRelease-1>", self.OnLetterButtonRelease)
        self.canvas.tag_bind("hand", "<B1-Motion>", self.OnLetterMotion)


#######################################################
#INITIALIZATION HELPERS
#######################################################
    def buildFrame(self):
        self.buttonDone = Button(self.frame, text="Finish play", 
                                 command=self.done_word, width=25)
        self.buttonSkip = Button(self.frame, 
                                 text="Skip turn (don't draw letters)", 
                                 command=self.skip, width=25)
        self.buttonReload = Button(self.frame, 
                                   text="Skip turn and draw new letters", 
                                   command=self.skip_and_draw, width=25)
        self.buttonForfeit = Button(self.frame, text="Forfeit game",
                                    command=self.forfeit, width=25)
        self.buttonUndoLetter = Button(self.frame, text="Undo letter",
                                       command=self.undoLetter, width=25)
        self.buttonUndoWord = Button(self.frame, text="Undo word",
                                     command=self.undoWord, width=25)
        self.buttonDone.grid(row=1, column=0)
        self.buttonSkip.grid(row=1,column=1)
        self.buttonReload.grid(row=2,column=0)
        self.buttonForfeit.grid(row=2,column=1)
        self.buttonUndoLetter.grid(row=3,column=0)
        self.buttonUndoWord.grid(row=3, column=1)
        scoreText = "Scoreboard\n"
        for player in self.players:
            scoreText += "%s: %d\n" % (player.name, player.score)
        self.scoreLabel = Label(self.frame, text=scoreText)
        self.scoreLabel.grid(row=0, columnspan=2)

    def createBoard(self):
        for i in range(15):
            for j in range(15):
                self.canvas.create_rectangle((25*i+12, 25*j+12, 25*i+37, 25*j+37), width=4.0,
                                             fill="brown", tags="border")
        for i in [1, 2, 3, 4, 10, 11, 12, 13]:
            self.canvas.create_text((25*i + 25, 25*i + 25), text='2W ', tags="board")
            self.canvas.create_text((25*i + 25, 25*(14-i) + 25), text='2W ', tags="board")
        self.canvas.create_text((200,200), text='2W ', tags="board")
        self.canvas.create_text((25, 25), text='3W ', tags="board")
        self.canvas.create_text((25, 200), text='3W ', tags="board")
        self.canvas.create_text((200, 25), text='3W ', tags="board")
        self.canvas.create_text((25, 375), text='3W ', tags="board")
        self.canvas.create_text((375, 25), text='3W ', tags="board")
        self.canvas.create_text((200,375), text='3W ', tags="board")
        self.canvas.create_text((375,200), text='3W ', tags="board")
        self.canvas.create_text((375, 375), text='3W ', tags="board")

        self.canvas.create_text((100, 25), text='2L ', tags="board")
        self.canvas.create_text((175, 75), text='2L ', tags="board")
        self.canvas.create_text((25, 100), text='2L ', tags="board")
        self.canvas.create_text((200,100), text='2L ', tags="board")
        self.canvas.create_text((75,175), text='2L ', tags="board")
        self.canvas.create_text((100,200), text='2L ', tags="board")
        self.canvas.create_text((175, 175), text='2L ', tags="board")

        self.canvas.create_text((300,25), text='2L ', tags="board")
        self.canvas.create_text((225,75), text='2L ', tags="board")
        self.canvas.create_text((375, 100), text='2L ', tags="board")
        self.canvas.create_text((225, 175), text='2L ', tags="board")
        self.canvas.create_text((325, 175), text='2L ', tags="board")
        self.canvas.create_text((300, 200), text='2L ', tags="board")

        self.canvas.create_text((100, 375), text='2L ', tags="board")
        self.canvas.create_text((175, 325), text='2L ', tags="board")
        self.canvas.create_text((25, 300), text='2L ', tags="board")
        self.canvas.create_text((75, 225), text='2L ', tags="board")
        self.canvas.create_text((175, 225), text='2L ', tags="board")
        self.canvas.create_text((200, 300), text='2L ', tags="board")

        self.canvas.create_text((300, 375), text='2L ', tags="board")
        self.canvas.create_text((225, 325), text='2L ', tags="board")
        self.canvas.create_text((375, 300), text='2L ', tags="board")
        self.canvas.create_text((325, 225), text='2L ', tags="board")
        self.canvas.create_text((225, 225), text='2L ', tags="board")
        
        self.canvas.create_text((150,50), text='3L ', tags="board")
        self.canvas.create_text((50,150), text='3L ', tags="board")
        self.canvas.create_text((150,150), text='3L ', tags="board")

        self.canvas.create_text((250,50), text='3L ', tags="board")
        self.canvas.create_text((250,150), text='3L ', tags="board")
        self.canvas.create_text((350,150), text='3L ', tags="board")

        self.canvas.create_text((250, 350), text='3L ', tags="board")
        self.canvas.create_text((350,250), text='3L ', tags="board")
        self.canvas.create_text((250,250), text='3L ', tags="board")

        self.canvas.create_text((50,250), text='3L ', tags="board")
        self.canvas.create_text((150,250), text='3L ', tags="board")
        self.canvas.create_text((150,350), text='3L ', tags="board")

    def createGame(self):
        self.bag = self.LetterBag()
        self.num_players = tkSimpleDialog.askinteger("Start Game", "How many players?", initialvalue=2)
        self.players = []
        self.current_player = 0
        self.mult_coords = {}
        self.blank_coords = []
        self.old_words = {}
        self.turn_items = []
        self.last_coord = (15,15)
        self.common_coord = ''
        self.first_turn = True
        for i in range(self.num_players):
            self.players.append(self.Player(self, "Player %d" % (i+1)))
        self.paint_hand(0)

########################################################
#BUTTON BINDING METHODS
########################################################
    def done_word(self):
        # calculate score, remove letters from canvas, draw new letters, paint new player's hand
        # update played letters to fixed letters
        if self.validatePlay() == True:
            self.players[self.current_player].reload()
            if len(self.players[self.current_player].hand) == 0:
                self.players[self.current_player].status = "playedout"
            self.calculateScore()
            self.mult_coords = {}
            self.turn_items = []
            self.last_coord = (15, 15)
            self.common_coord = ''
            self.canvas.delete("hand")
            self.canvas.delete("other")
            self.change_player()
            self.paint_hand(self.current_player)
            self.canvas.addtag_withtag("fixed", "played")
            self.canvas.dtag("played")
        else:
            if self.first_turn == True:
                tkMessageBox.showerror("Error", "One letter must be on center (2W) space")
            self.undoWord()

    def skip(self):
        self.change_player()
        self.canvas.delete("hand")
        self.canvas.delete("other")
        self.paint_hand(self.current_player)

    def skip_and_draw(self):
        result = self.players[self.current_player].swap()
        if result:
            tkMessageBox.showwarning("Warning", "Could not draw new letters. Pick another option.")
            return
        else:
            self.change_player()
            self.canvas.delete("hand")
            self.canvas.delete("other")
            self.paint_hand(self.current_player)

    def forfeit(self):
        if tkMessageBox.askokcancel("Forfeit", "Are you sure you want to remove yourself from the game?"):
            print "Player " + str(self.current_player + 1) + " has quit."
            self.players[self.current_player].status = "forfeited"
            self.players[self.current_player].quit()
            scoreText = "Scoreboard\n"
            for player in self.players:
                scoreText += "%s: %d " % (player.name, player.score)
                if player.status == "forfeited":
                    scoreText += "(forfeited)\n"
                elif player.status == "playedout":
                    scoreText += "(out of letters)"
                else:
                    scoreText += "\n"
            self.scoreLabel.config(text=scoreText)
            self.skip()
        pass

    def undoLetter(self):
        # delete item from turn_items
        # repaint hand

        #get letter item from turn_items list
        letterToUndo = self.turn_items.pop()
        #get board coordinates of letter
        pos = self.canvas.coords(letterToUndo)
        x = round((pos[0] - 25) / 25)
        y = round((pos[1] - 25) / 25)
        posTup = (x, y)
        # return a blank tile to the hand if the letter played was originally blank
        if posTup in self.blank_coords:
            playedLetter = '[]'
            self.blank_coords.remove(posTup)
        else:
            playedLetter = self.canvas.itemcget(letterToUndo, "text").strip().lower()
        self.players[self.current_player].hand.append(playedLetter)
        if len(self.players[self.current_player].hand) == 7:
            self.last_coord = (15,15)
            self.common_coord = ''
        #erase hand and letter from board
        self.canvas.delete(letterToUndo)
        self.canvas.delete("hand")
        self.canvas.delete("other")
        #repaint player's hand
        self.paint_hand(self.current_player)
        #repaint multiplier on board if it was originally on the space
        if posTup in self.mult_coords.keys():
            mult = self.mult_coords[posTup]
            self.canvas.create_text(pos, text=mult+' ')

    def undoWord(self):
        #delete all items from turn_items and reset valid letter placement variables
        for i in range(len(self.turn_items)):
            self.undoLetter()
        self.last_coord = (15, 15)
        self.common_coord = ''

    def change_player(self):
        activePlayer = False
        count = 0
        while (activePlayer == False):
            if (count > self.num_players):
                text = ""
                for player in self.players:
                    text += "%s: %d\n" % (player.name, player.score)
                tkMessageBox.showinfo("Game over!", text)
                break;
            self.current_player = (self.current_player + 1) % self.num_players
            activePlayer = self.players[self.current_player].isActive()
            count += 1
        self.first_turn = False
        tkMessageBox.showinfo("New Turn", "Player %s's turn!" % str(self.current_player+1))

#######################################################
#SCORE CALCULATION METHODS
#######################################################
    def validatePlay(self):
        words = self.find_all()
        # print "These are all the words on the board:"
        # print words
        for word in words:
            if word not in self.VALID_WORDS:
                tkMessageBox.showerror("Error", word + " not a valid word.")
                return False
        common_words = {}
        for key in self.old_words.keys():
            if key in words.keys():
                if self.old_words[key] == words[key]:
                    common_words[key] = words[key]
        # print "These are all the words not played this turn:"
        # print common_words
        words_copy = copy.deepcopy(words)
        #self.old_words = words_copy
        for key in common_words:
            if common_words[key] == words[key]:
                words.pop(key)
        
        # print "Validating these words:"
        # print words
        validPlay = False
        for word in words:
            # print "Testing length..."
            if len(word) < 2:
                # print "invalid. too short"
                return False
            #test if it shares any coordinates with old words
            # print "Testing coordinate sharing..."
            for coord in words[word]:
                if coord == (7,7):
                    # print "valid"
                    return True
                for old_word in self.old_words:
                    for old_coord in self.old_words[old_word]:
                        if coord == old_coord:
                            # print "valid"
                            return True
        # print "invalid. no shared coordinates"
        return False
        pass

    def calculateScore(self):
        # calculate the score for the turn
        # uses the multiplier coordinates dict and old words dict to find new words and their
        # multipliers. 
        #first: search through board to find all words
        #put all words in words dict
        #compare with self.old_words
        #find common words between the two
        #make self.old_words equal to a copy of words dict
        #delete all common words from words dict
        # print "Calculating score..."
        words = self.find_all()
        # print "self.find_all():"
        # print words
        # print "self.old_words:"
        # print self.old_words
        common_words = {}
        for key in self.old_words.keys():
            if key in words.keys():
                if self.old_words[key] == words[key]:
                    common_words[key] = words[key]
        words_copy = copy.deepcopy(words)
        # self.old_words = words_copy
        for key in common_words:
            if common_words[key] == words[key]:
                words.pop(key)
        # print "Using these words:"
        # print words
        play_score = 0
        for key in words:
            word_score = 0
            # print key
            dubWord, tripWord = False, False
            for i in range(len(key)):
                value = self.WORD_VALUES[key[i].lower()]
                coord = words[key][i]
                if coord in self.mult_coords.keys():
                    mult = self.mult_coords[coord]
                    if mult == "2L":
                        value *= 2
                    elif mult == "3L":
                        value *= 3
                    elif mult == "2W":
                        dubWord = True
                    elif mult == "3W":
                        tripWord = True
                if coord in self.blank_coords:
                    value = 0
                    # print "Found a blank tile"
                # print "Found value for letter: " + str(value)
                word_score += value
            if dubWord:
                word_score *= 2
            elif tripWord:
                word_score *= 3
            play_score += word_score

        # print "Calculated score " + str(play_score)

        #update score label
        self.players[self.current_player].score += play_score
        scoreText = "Scoreboard\n"
        for player in self.players:
            scoreText += "%s: %d " % (player.name, player.score)
            if player.status == "forfeited":
                scoreText += "(forfeited)\n"
            elif player.status == "playedout":
                scoreText += "(out of letters)\n"
            else:
                scoreText += "\n"
        self.scoreLabel.config(text=scoreText)
        self.old_words = words_copy

    def find_all(self):
        words = {}
        for i in range(15):
            for j in range(15):
                #test only the spaces which have letters
                x, y = 25*i+25, 25*j+25
                if self.containsLetter(i, j):
                    startsWord = self.isBeginning(i, j)
                    if startsWord.count('r') > 0:
                        #loop to find word going right
                        wordFound = False
                        word = self.getLetter(i, j).strip()
                        coords = [(i, j)]
                        ii = i
                        while (wordFound == False):
                            if ii < 14:
                                if self.containsLetter(ii+1, j):
                                    word += self.getLetter(ii+1, j).strip()
                                    coords.append((ii+1, j))
                                elif self.containsLetter(ii+1, j) == False:
                                    wordFound = True
                                ii += 1
                            elif ii >= 14:
                                wordFound = True
                        words[word] = coords
                    if startsWord.count('d') > 0:
                        #loop to find word going down
                        wordFound = False
                        word = self.getLetter(i, j).strip()
                        coords = [(i, j)]
                        jj = j
                        while (wordFound == False):
                            if jj < 14:
                                if self.containsLetter(i, jj+1):
                                    word += self.getLetter(i, jj+1).strip()
                                    coords.append((i, jj+1))
                                elif self.containsLetter(i, jj+1) == False:
                                    wordFound = True
                                jj += 1
                            elif jj >= 14:
                                wordFound = True
                        words[word] = coords
        return words
        

    def getLetter(self, i, j):
        #returns the letter at board coordinates (when known that that space has a letter)
        x, y = 25*i+25, 25*j+25
        overlaps = self.canvas.find_overlapping(x-5,y-5,x+5,y+5)
        return self.canvas.itemcget(overlaps[1], "text")

    #tests if a board coordinate contains a played letter
    def containsLetter(self, i, j):
        x, y = 25*i+25, 25*j+25
        overlaps = self.canvas.find_overlapping(x-5,y-5,x+5,y+5)
        if len(overlaps) > 1:
            text = self.canvas.itemcget(overlaps[1], "text")
            if text not in ("2L ", "2W ", "3L ", "3W "):
                return True
            else:
                return False
        return False

    def isBeginning(self, i, j):
        wordDown = False
        wordRight = False
        result = ''
        if (i == 0 and j == 0):
            # will always be the start of a word
            tileLeft = False
            tileAbove = False
            if self.containsLetter(i+1, j):
                wordRight = True
            if self.containsLetter(i, j+1):
                wordDown = True
        elif (i == 0):
            #along left
            #if there is a tile above it, it's not the start of a word
            #otherwise it is
            tileLeft = False
            tileAbove = self.containsLetter(i, j-1)
        elif (j == 0):
            #along top
            #if there is a tile to its left, it's not the start of a word
            #otherwise it is
            tileLeft = self.containsLetter(i-1, j)
            tileAbove = False
        else:
            tileAbove = self.containsLetter(i, j-1)
            tileLeft = self.containsLetter(i-1, j)
        if tileAbove == False and tileLeft == False:
            #if not along right wall, check for letters on right
            if (i < 14):
                wordRight = self.containsLetter(i+1,j)
            #if not on bottom, check for letters below
            if (j < 14):
                wordDown = self.containsLetter(i,j+1)
        elif tileAbove == False:
            if (j < 14):
                wordDown = self.containsLetter(i,j+1)
        elif tileLeft == False:
            if (i < 14):
                wordRight = self.containsLetter(i+1, j)
        if wordDown and wordRight:
            return 'rd'
        elif wordDown:
            return 'd'
        elif wordRight:
            return 'r'
        else:
            return ''


    

######################################################
#LETTER DRAGGING METHODS
######################################################
    def OnLetterButtonPress(self, event):

        self._drag_data["item"] = self.canvas.find_closest(event.x, event.y)[0]
        self.canvas.tag_raise(self._drag_data["item"])
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self._drag_data["xStart"] = event.x
        self._drag_data["yStart"] = event.y

    def OnLetterButtonRelease(self, event):
        x = event.x
        y = event.y
        #remove justplayed tag
        self.canvas.dtag("justPlayed")
        # find all overlapping elements on the Canvas
        overlaps = self.canvas.find_overlapping(x - 5, y - 5, x + 5, y + 5)
        try:
            space = overlaps[1]
        # if there's only one overlap, it is the dragged character which was placed off board
        # in this case, return letter and start over
        except IndexError:
            tkMessageBox.showerror("Error",  "Tried to place tile off board. Try again.")
            deltaX = self._drag_data["xStart"] - self._drag_data["x"]
            deltaY = self._drag_data["yStart"] - self._drag_data["y"]
            self.canvas.move(self._drag_data["item"], deltaX, deltaY)
            return
        overlaps = overlaps[1:]
        tags = []
        for thing in overlaps:
            tags = self.canvas.itemcget(thing, "tags")
        # if a border overlaps, that's not a valid placement
        if "border" in tags:
            tkMessageBox.showerror("Error", "Tried to place tile on a border. Try again.")
            deltaX = self._drag_data["xStart"] - self._drag_data["x"]
            deltaY = self._drag_data["yStart"] - self._drag_data["y"]
            self.canvas.move(self._drag_data["item"], deltaX, deltaY)
            return
        # if a played tile overlaps, that's not a valid placement
        elif "played" in tags or "fixed" in tags:
            tkMessageBox.showerror("Error", "Tried to place tile on a used space. Try again.")
            deltaX = self._drag_data["xStart"] - self._drag_data["x"]
            deltaY = self._drag_data["yStart"] - self._drag_data["y"]
            self.canvas.move(self._drag_data["item"], deltaX, deltaY)
            return
        else:
            try:
                tile = self.canvas.itemcget(space, "text")
            except TclError:
                tkMessageBox.showerror("Error", "An error occurred. Bug life. Try again.")
                deltaX = self._drag_data["xStart"] - self._drag_data["x"]
                deltaY = self._drag_data["yStart"] - self._drag_data["y"]
                self.canvas.move(self._drag_data["item"], deltaX, deltaY)
                return
            stuff = self._drag_data["item"]
            letterMoved = self.canvas.itemcget(stuff, "text")
            # if the overlap is the letter being moved, place it on the board
            if tile == letterMoved:
                new_x = int(25 * round(x / 25.0))
                new_y = int(25 * round(y / 25.0))
                coords = ((new_x - 25) / 25, (new_y - 25) / 25)
                #if shared coordinate hasn't been set yet, set it by comparing to last coordinate
                if self.common_coord == '':
                    # if this is not the first letter of the play (it must be the second), set the common coordinate
                    if coords[0] == self.last_coord[0]:
                        self.common_coord = 'x'
                    elif coords[1] == self.last_coord[1]:
                        self.common_coord = 'y'
                    # if this is the first letter of the play, set the last coordinate
                    # elif 15 in self.last_coord:
                    #     self.last_coord = coords
                # if the placement shares no coordinates with the last letter, it is definitely invalid placement
                elif coords[0] not in self.last_coord and coords[1] not in self.last_coord:
                    tkMessageBox.showerror("Error", "Illegal letter placement. Try again.")
                    deltaX = self._drag_data["xStart"] - self._drag_data["x"]
                    deltaY = self._drag_data["yStart"] - self._drag_data["y"]
                    self.canvas.move(self._drag_data["item"], deltaX, deltaY)
                    return
                #else it is invalid if it shares a coordinate, but it's the wrong one
                elif coords[1] != self.last_coord[1] and self.common_coord == 'y':
                    tkMessageBox.showerror("Error", "Illegal letter placement. Try again.")
                    deltaX = self._drag_data["xStart"] - self._drag_data["x"]
                    deltaY = self._drag_data["yStart"] - self._drag_data["y"]
                    self.canvas.move(self._drag_data["item"], deltaX, deltaY)
                    return
                elif coords[0] != self.last_coord[0] and self.common_coord == 'x':
                    tkMessageBox.showerror("Error", "Illegal letter placement. Try again.")
                    deltaX = self._drag_data["xStart"] - self._drag_data["x"]
                    deltaY = self._drag_data["yStart"] - self._drag_data["y"]
                    self.canvas.move(self._drag_data["item"], deltaX, deltaY)
                    return
                self.last_coord = coords

                letterMoved = letterMoved.strip()
                letterDuplicate = copy.deepcopy(letterMoved)
                if letterMoved == '[]':
                    letterMoved = tkSimpleDialog.askstring("Blank Tile", "Which letter would you like to use?")
                    letterMoved = letterMoved.upper()
                if letterDuplicate == '[]':
                    self.blank_coords.append(coords)
                item = self.canvas.create_text((new_x, new_y), 
                                               text=letterMoved, tags="played", fill="white")
                self.turn_items.append(item)
                self.players[self.current_player].hand.remove(letterDuplicate.lower().strip())
                # get rid of extra copy of letter this creates
                self.canvas.delete(stuff)
            # else, it must be a multiplier effect space. place it on the board
            else:
                new_x = int(25 * round(x / 25.0))
                new_y = int(25 * round(y / 25.0))
                coords = ((new_x - 25) / 25, (new_y - 25) / 25)
                #if shared coordinate hasn't been set yet, set it by comparing to last coordinate
                if self.common_coord == '':
                    # if this is not the first letter of the play (it must be the second), set the common coordinate
                    if 15 not in self.last_coord:
                        if coords[0] == self.last_coord[0]:
                            self.common_coord = 'x'
                        elif coords[1] == self.last_coord[1]:
                            self.common_coord = 'y'
                    # if this is the first letter of the play, set the last coordinate
                    # elif 15 in self.last_coord:
                    #     self.last_coord = coords
                # if the placement shares no coordinates with the last letter, it is definitely invalid placement
                elif coords[0] not in self.last_coord and coords[1] not in self.last_coord:
                    tkMessageBox.showerror("Error", "Illegal letter placement. Try again.")
                    deltaX = self._drag_data["xStart"] - self._drag_data["x"]
                    deltaY = self._drag_data["yStart"] - self._drag_data["y"]
                    self.canvas.move(self._drag_data["item"], deltaX, deltaY)
                    return
                #else it is invalid if it shares a coordinate, but it's the wrong one
                elif coords[1] != self.last_coord[1] and self.common_coord == 'y':
                    tkMessageBox.showerror("Error", "Illegal letter placement. Try again.")
                    deltaX = self._drag_data["xStart"] - self._drag_data["x"]
                    deltaY = self._drag_data["yStart"] - self._drag_data["y"]
                    self.canvas.move(self._drag_data["item"], deltaX, deltaY)
                    return
                elif coords[0] != self.last_coord[0] and self.common_coord == 'x':
                    tkMessageBox.showerror("Error", "Illegal letter placement. Try again.")
                    deltaX = self._drag_data["xStart"] - self._drag_data["x"]
                    deltaY = self._drag_data["yStart"] - self._drag_data["y"]
                    self.canvas.move(self._drag_data["item"], deltaX, deltaY)
                    return
                self.last_coord = coords
                #print "self.common_coord: "
                #print self.common_coord

                letterMoved = letterMoved.strip()
                letterDuplicate = copy.deepcopy(letterMoved)
                if letterMoved == '[]':
                    letterMoved = tkSimpleDialog.askstring("Blank Tile", "Which letter would you like to use?")
                    letterMoved = letterMoved.upper()
                self.canvas.delete(space)
                self.canvas.delete(space)
                self.mult_coords[coords] = tile.strip()
                if letterDuplicate == '[]':
                    self.blank_coords.append(coords)
                item = self.canvas.create_text((new_x,new_y), 
                                               text=letterMoved, tags="played", fill="white")
                self.turn_items.append(item)
                self.players[self.current_player].hand.remove(letterDuplicate.lower().strip())
                self.canvas.delete(stuff)
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def OnLetterMotion(self, event):
        deltaX = event.x - self._drag_data["x"]
        deltaY = event.y - self._drag_data["y"]

        self.canvas.move(self._drag_data["item"], deltaX, deltaY)

        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

#############################################
#OTHER METHODS
#############################################
    def paint_hand(self, i):
        hand = self.players[i].hand
        self.canvas.create_text((75, 425), text="Player %d's turn" % (self.current_player + 1), tags="other")
        for i in range(len(hand)):
            self.canvas.create_text((25*i+25,450), text=hand[i].upper() + ' ', tags="hand")
            self.canvas.create_text((25*i+25, 475), text=self.WORD_VALUES[hand[i]], tags="other")

root = Tk()

game = Game(root)

root.mainloop()

#eventually: alter the game to make it diff/your own: words with fiends??
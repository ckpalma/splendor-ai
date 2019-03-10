from enum import Enum
import random
import copy

random.seed(None)

def setSeed(s):
    random.seed(s)

"""
Basic enumerated class to specify colors when needed.
"""
class Color(Enum):
    WHITE = 0
    BLACK = 1
    GREEN = 2
    RED = 3
    BLUE = 4
    GOLD = 5
    
    @classmethod
    def mapToColor(self, color):
        if (color == "W"):
            return Color.WHITE
        elif (color == "K"):
            return Color.BLACK
        elif (color == "E"):
            return Color.GREEN
        elif (color == "R"):
            return Color.RED
        elif (color == "B"):
            return Color.BLUE
        elif (color == "G"):
            return Color.GOLD
        else:
            return None
    
    def __str__(self):
        s = ""
        if self.value == 1:
            s = "W"
        elif self.value == 2:
            s = "K"
        elif self.value == 3:
            s = "E"
        elif self.value == 4:
            s = "R"
        elif self.value == 5:
            s = "B"
        elif self.value == 6:
            s = "G"
        return s

"""
Basic enumerated class to specify whether a player is a human or AI.
"""
class PlayerType(Enum):
    HUMAN = 1
    AI = 2

"""
A GemDict is a dictionary with Color keys and int values. Dictionary can be accessed through the getter.
"""
class GemDict:
    def __init__(self, gem_lst):
        self.data = {
            Color.WHITE : gem_lst[0],
            Color.BLACK : gem_lst[1],
            Color.GREEN : gem_lst[2],
            Color.RED   : gem_lst[3],
            Color.BLUE  : gem_lst[4]}

    def add(self, color, num):
        if color == Color.WHITE:
            self.data[Color.WHITE] += num
            
        elif color == Color.BLACK:
            self.data[Color.BLACK] += num

        elif color == Color.GREEN:
            self.data[Color.GREEN] += num
            
        elif color == Color.RED:
            self.data[Color.RED]   += num
            
        elif color == Color.BLUE:
            self.data[Color.BLUE]  += num
            
        else:
            raise ValueError

    def remove(self, color, num):
        if color == Color.WHITE:
            self.data[Color.WHITE] -= num
            
        elif color == Color.BLACK:
            self.data[Color.BLACK] -= num

        elif color == Color.GREEN:
            self.data[Color.GREEN] -= num
            
        elif color == Color.RED:
            self.data[Color.RED]   -= num
            
        elif color == Color.BLUE:
            self.data[Color.BLUE]  -= num
            
        else:
            raise ValueError

    def total_gems(self):
        return (
            self.data[Color.WHITE]  +
            self.data[Color.BLACK]  +
            self.data[Color.GREEN]  +
            self.data[Color.RED]    +
            self.data[Color.BLUE])

    def get_data(self):
        return self.data
    
    def data_gui(self):
        return [
            self.data[Color.WHITE],
            self.data[Color.BLACK],
            self.data[Color.GREEN],
            self.data[Color.RED],
            self.data[Color.BLUE]]
    
    def addGD(self, gd):
        w = self.data_gui()[0] + gd.data_gui()[0]
        k = self.data_gui()[1] + gd.data_gui()[1]
        e = self.data_gui()[2] + gd.data_gui()[2]
        r = self.data_gui()[3] + gd.data_gui()[3]
        b = self.data_gui()[4] + gd.data_gui()[4]
        return self.gdString(w,k,e,r,b)
    
    def gdString(self,w,k,e,r,b):
        return (str(w)+"|"+str(k)+"|"+str(e)+"|"+str(r)+"|"+str(b))
    
    def __str__(self):
        w = self.data_gui()[0]
        k = self.data_gui()[1]
        e = self.data_gui()[2]
        r = self.data_gui()[3]
        b = self.data_gui()[4]
        return self.gdString(w,k,e,r,b)

"""
    A State will contain:

    current_player: A Player object of the player who's turn it currently is
    players: A list of Player objects, in turn order, corresponding to each player in the game
    tier1_deck: a list of Card objects that make up the remaining cards in the tier 1 deck
    tier2_deck: a list of Card objects that make up the remaining cards in the tier 2 deck
    tier3_deck: a list of Card objects that make up the remaining cards in the tier 3 deck
    tier1: a list of Card objects that represent the tier 1 cards available for purchase
    tier2: a list of Card objects that represent the tier 2 cards available for purchase
    tier3: a list of Card objects that represent the tier 3 cards available for purchase
    available_gems: a GemDict representing the number of gems available to take
    gold: an int, the number of gold gems available to take
    nobles: a list of GemDicts representing the nobles available for purchase (each noble is worth 3 points)
"""
class State:
    """
    Sets up the initial state of the game with a randomized board and gems for the correct number of players. 
    """
    def __init__(self, num_human_players, num_AI_players):
        self._players = []
        for i in range(num_human_players):
            self._players.append(Player(PlayerType.HUMAN, "HUMAN " + str(i)))
        for j in range(num_AI_players):
            self._players.append(Player(PlayerType.AI, "AI " + str(j)))
        random.shuffle(self._players) #put players in random order
        
        self._current_player = self._players[0] #set current player to first player in list
        
        if num_AI_players+num_human_players == 2:
            self._available_gems = GemDict([4,4,4,4,4])
        elif num_human_players + num_human_players == 3:
            self._available_gems = GemDict([5,5,5,5,5])
        else:
            self._available_gems = GemDict([7,7,7,7,7])
        
        self._gold = 5
        
        self._tier1_deck = self.gen_tier1()
        self._tier2_deck = self.gen_tier2()
        self._tier3_deck = self.gen_tier3()
        random.shuffle(self._tier1_deck)
        random.shuffle(self._tier2_deck)
        random.shuffle(self._tier3_deck)
        
        self._tier1 = self._tier1_deck[:4]
        self._tier2 = self._tier2_deck[:4]
        self._tier3 = self._tier3_deck[:4]
        
        self._tier1_deck = self._tier1_deck[4:]
        self._tier2_deck = self._tier2_deck[4:]
        self._tier3_deck = self._tier3_deck[4:]

        self._nobles = self.gen_nobles()
        random.shuffle(self._nobles)
        self._nobles = self._nobles[:(num_human_players+num_AI_players+1)] #num nobles available = num players + 1
        self._turnCount = 1
        self._discarding = False
        self._firstWinner = None
        self._winners = []
        self._running = True
        self._interactions = 0

    """Generates a shuffled deck of tier 1 cards."""
    def gen_tier1(self):
        tier1_deck = []
        tier1_deck.append(Card(Color.BLACK, 0, [1, 0, 1, 1, 1], 1))
        tier1_deck.append(Card(Color.BLACK, 0, [0, 0, 2, 1, 0], 1))
        tier1_deck.append(Card(Color.BLACK, 0, [2, 0, 2, 0, 0], 1))
        tier1_deck.append(Card(Color.BLACK, 0, [0, 1, 1, 3, 0], 1))
        tier1_deck.append(Card(Color.BLACK, 0, [0, 0, 3, 0, 0], 1))
        tier1_deck.append(Card(Color.BLACK, 0, [1, 0, 1, 1, 2], 1))
        tier1_deck.append(Card(Color.BLACK, 0, [2, 0, 0, 1, 2], 1))
        tier1_deck.append(Card(Color.BLACK, 1, [0, 0, 0, 0, 4], 1))

        tier1_deck.append(Card(Color.BLUE, 0, [1, 2, 0, 0, 0], 1))
        tier1_deck.append(Card(Color.BLUE, 0, [1, 1, 1, 2, 0], 1))
        tier1_deck.append(Card(Color.BLUE, 0, [1, 1, 1, 1, 0], 1))
        tier1_deck.append(Card(Color.BLUE, 0, [0, 0, 3, 1, 1], 1))
        tier1_deck.append(Card(Color.BLUE, 0, [0, 3, 0, 0, 0], 1))
        tier1_deck.append(Card(Color.BLUE, 0, [1, 0, 2, 2, 0], 1))
        tier1_deck.append(Card(Color.BLUE, 0, [0, 2, 2, 0, 0], 1))
        tier1_deck.append(Card(Color.BLUE, 1, [0, 0, 0, 4, 0], 1))

        tier1_deck.append(Card(Color.GREEN, 0, [2, 0, 0, 0, 1], 1))
        tier1_deck.append(Card(Color.GREEN, 0, [0, 0, 0, 2, 2], 1))
        tier1_deck.append(Card(Color.GREEN, 0, [1, 0, 1, 0, 3], 1))
        tier1_deck.append(Card(Color.GREEN, 0, [1, 1, 0, 1, 1], 1))
        tier1_deck.append(Card(Color.GREEN, 0, [1, 1, 0, 1, 2], 1))
        tier1_deck.append(Card(Color.GREEN, 0, [0, 2, 0, 2, 1], 1))
        tier1_deck.append(Card(Color.GREEN, 0, [0, 0, 0, 3, 0], 1))
        tier1_deck.append(Card(Color.GREEN, 1, [0, 4, 0, 0, 0], 1))

        tier1_deck.append(Card(Color.RED, 0, [3, 0, 0, 0, 0], 1))
        tier1_deck.append(Card(Color.RED, 0, [1, 3, 0, 1, 0], 1))
        tier1_deck.append(Card(Color.RED, 0, [0, 0, 1, 0, 2], 1))
        tier1_deck.append(Card(Color.RED, 0, [2, 2, 1, 0, 0], 1))
        tier1_deck.append(Card(Color.RED, 0, [2, 1, 1, 0, 1], 1))
        tier1_deck.append(Card(Color.RED, 0, [1, 1, 1, 0, 1], 1))
        tier1_deck.append(Card(Color.RED, 0, [2, 0, 0, 2, 0], 1))
        tier1_deck.append(Card(Color.RED, 1, [4, 0, 0, 0, 0], 1))

        tier1_deck.append(Card(Color.WHITE, 0, [0, 1, 2, 0, 2], 1))
        tier1_deck.append(Card(Color.WHITE, 0, [0, 1, 0, 2, 0], 1))
        tier1_deck.append(Card(Color.WHITE, 0, [0, 1, 1, 1, 1], 1))
        tier1_deck.append(Card(Color.WHITE, 0, [0, 0, 0, 0, 3], 1))
        tier1_deck.append(Card(Color.WHITE, 0, [0, 0, 2, 0, 2], 1))
        tier1_deck.append(Card(Color.WHITE, 0, [0, 1, 2, 1, 1], 1))
        tier1_deck.append(Card(Color.WHITE, 0, [3, 1, 0, 0, 1], 1))
        tier1_deck.append(Card(Color.WHITE, 1, [0, 0, 4, 0, 0], 1))
        return tier1_deck

    """Generates a shuffled deck of tier 2 cards."""
    def gen_tier2(self):
        tier2_deck = []
        tier2_deck.append(Card(Color.BLACK, 1, [3, 0, 2, 0, 2], 2))
        tier2_deck.append(Card(Color.BLACK, 1, [3, 2, 3, 0, 0], 2))
        tier2_deck.append(Card(Color.BLACK, 2, [0, 0, 4, 2, 1], 2))
        tier2_deck.append(Card(Color.BLACK, 2, [5, 0, 0, 0, 0], 2))
        tier2_deck.append(Card(Color.BLACK, 2, [0, 0, 5, 3, 0], 2))
        tier2_deck.append(Card(Color.BLACK, 3, [0, 6, 0, 0, 0], 2))

        tier2_deck.append(Card(Color.BLUE, 1, [0, 0, 2, 3, 2], 2))
        tier2_deck.append(Card(Color.BLUE, 1, [0, 3, 3, 0, 2], 2))
        tier2_deck.append(Card(Color.BLUE, 2, [5, 0, 0, 0, 3], 2))
        tier2_deck.append(Card(Color.BLUE, 2, [0, 0, 0, 0, 5], 2))
        tier2_deck.append(Card(Color.BLUE, 2, [2, 4, 0, 1, 0], 2))
        tier2_deck.append(Card(Color.BLUE, 3, [0, 0, 0, 0, 6], 2))

        tier2_deck.append(Card(Color.GREEN, 1, [3, 0, 2, 3, 0], 2))
        tier2_deck.append(Card(Color.GREEN, 1, [2, 2, 0, 0, 3], 2))
        tier2_deck.append(Card(Color.GREEN, 2, [4, 1, 0, 0, 2], 2))
        tier2_deck.append(Card(Color.GREEN, 2, [0, 0, 5, 0, 0], 2))
        tier2_deck.append(Card(Color.GREEN, 2, [0, 0, 3, 0, 5], 2))
        tier2_deck.append(Card(Color.GREEN, 3, [0, 0, 6, 0, 0], 2))

        tier2_deck.append(Card(Color.RED, 1, [0, 3, 0, 2, 3], 2))
        tier2_deck.append(Card(Color.RED, 1, [2, 3, 0, 2, 0], 2))
        tier2_deck.append(Card(Color.RED, 2, [1, 0, 2, 0, 4], 2))
        tier2_deck.append(Card(Color.RED, 2, [3, 5, 0, 0, 0], 2))
        tier2_deck.append(Card(Color.RED, 2, [0, 5, 0, 0, 0], 2))
        tier2_deck.append(Card(Color.RED, 3, [0, 0, 0, 6, 0], 2))

        tier2_deck.append(Card(Color.WHITE, 1, [0, 2, 3, 2, 0], 2))
        tier2_deck.append(Card(Color.WHITE, 1, [2, 0, 0, 3, 3], 2))
        tier2_deck.append(Card(Color.WHITE, 2, [0, 2, 1, 4, 0], 2))
        tier2_deck.append(Card(Color.WHITE, 2, [0, 0, 0, 5, 0], 2))
        tier2_deck.append(Card(Color.WHITE, 2, [0, 3, 0, 5, 0], 2))
        tier2_deck.append(Card(Color.WHITE, 3, [6, 0, 0, 0, 0], 2))

        return tier2_deck
    """Generates a shuffled deck of tier 3 cards."""
    def gen_tier3(self):
        tier3_deck = []
        tier3_deck.append(Card(Color.BLACK, 3, [3, 0, 5, 3, 3], 3))
        tier3_deck.append(Card(Color.BLACK, 4, [0, 0, 0, 7, 0], 3))
        tier3_deck.append(Card(Color.BLACK, 4, [0, 3, 3, 6, 0], 3))
        tier3_deck.append(Card(Color.BLACK, 5, [0, 3, 0, 7, 0], 3))

        tier3_deck.append(Card(Color.BLUE, 3, [3, 5, 3, 3, 0], 3))
        tier3_deck.append(Card(Color.BLUE, 4, [7, 0, 0, 0, 0], 3))
        tier3_deck.append(Card(Color.BLUE, 4, [6, 3, 0, 0, 3], 3))
        tier3_deck.append(Card(Color.BLUE, 5, [7, 0, 0, 0, 3], 3))

        tier3_deck.append(Card(Color.GREEN, 3, [5, 3, 0, 3, 3], 3))
        tier3_deck.append(Card(Color.GREEN, 4, [3, 0, 3, 0, 6], 3))
        tier3_deck.append(Card(Color.GREEN, 4, [0, 0, 0, 0, 7], 3))
        tier3_deck.append(Card(Color.GREEN, 5, [0, 0, 3, 0, 7], 3))

        tier3_deck.append(Card(Color.RED, 3, [3, 3, 3, 0, 5], 3))
        tier3_deck.append(Card(Color.RED, 4, [0, 0, 7, 0, 0], 3))
        tier3_deck.append(Card(Color.RED, 4, [0, 0, 6, 3, 3], 3))
        tier3_deck.append(Card(Color.RED, 5, [0, 0, 7, 3, 0], 3))

        tier3_deck.append(Card(Color.WHITE, 3, [0, 3, 3, 5, 3], 3))
        tier3_deck.append(Card(Color.WHITE, 4, [0, 7, 0, 0, 0], 3))
        tier3_deck.append(Card(Color.WHITE, 4, [3, 6, 0, 3, 0], 3))
        tier3_deck.append(Card(Color.WHITE, 5, [3, 7, 0, 0, 0], 3))
        return tier3_deck

    def gen_nobles(self):
        nobles = []
        nobles.append(GemDict([0,0,4,4,0]))
        nobles.append(GemDict([3,3,0,3,0]))
        nobles.append(GemDict([4,0,0,0,4]))
        nobles.append(GemDict([4,4,0,0,0]))
        nobles.append(GemDict([0,0,4,0,4]))
        nobles.append(GemDict([0,0,3,3,3]))
        nobles.append(GemDict([3,0,3,0,3]))
        nobles.append(GemDict([0,4,0,4,0]))
        nobles.append(GemDict([3,3,0,0,3]))
        nobles.append(GemDict([0,3,3,3,0]))
        return nobles
    """
    Returns whether the game has finished.
    """
    def running(self):
        return self._running
    """
    Set _running to False.
    """
    def endGame(self):
        self._running = False
    """
    Returns the turn count for the game.
    """
    def get_turn_count(self):
        return self._turnCount
    """
    Returns a list of Player objects, in turn order, corresponding to each player in the game.
    """
    def get_players(self):
        return self._players
    """
    Returns a Player object of the current player.
    """
    def get_current_player(self):
        return self._current_player

    """
    Returns the remaining tier1 cards left in the deck as a list of Card objects.
    """
    def get_tier1_deck(self):
        return self._tier1_deck

    """
    Returns the remaining tier2 cards left in the deck as a list of Card objects.
    """
    def get_tier2_deck(self):
        return self._tier2_deck

    """
    Returns the remaining tier3 cards left in the deck as a list of Card objects.
    """
    def get_tier3_deck(self):
        return self._tier3_deck

    """
    Returns the remaining tier1 cards currently on the board as a list of Card objects.
    """
    def get_tier1(self):
        return self._tier1

    """
    Returns the remaining tier2 cards currently on the board as a list of Card objects.
    """
    def get_tier2(self):
        return self._tier2

    """
    Returns the tier3 cards currently on the board as a list of Card objects.
    """
    def get_tier3(self):
        return self._tier3

    """
    Returns the gems available to take as a GemDict object.
    """
    def get_avail_gems(self):
        return self._available_gems

    """
    Returns int of the number of gold gems still available.
    """
    def get_num_gold(self):
        return self._gold

    """
    Returns the nobles remaining on the board.
    """
    def get_nobles(self):
        return self._nobles
    
    def getNoble(self, noble):
        return self._nobles[noble]
    
    def getPlayerReserved(self, player, card):
        self._players[player].get_reserved()[card].reserve(card)
        return self._players[player].get_reserved()[card]
    
    """
    Returns the index of the current player in the order the players are in.
    """
    def current_player_index(self):
        return self._players.index(self._current_player)
    
    """
    Changes the current player to the next player in the player list.
    """
    def next_player(self):
        current = self.current_player_index()
        self._current_player = self._players[current+1-len(self._players)]
        self._turnCount += 1

    """
    Removes one card from the desired tier deck and adds it to the tier cards on the board. 
    
    tier:   Int. The tier number whose deck a card should be removed from. Also the tier number 
            on the board that the card will be added to.
            If tier = 1, remove from tier 1 deck. If tier = 2, remove from tier 2 deck. 
            If tier = 3, remove from tier 3 deck. Otherwise the method raises ValueError.

    This method is called after a player purchases a card to replenish the cards on the board.
    If there are no cards remaining in the desired tier deck, no card is added to the board. 
    """
    def draw_from_deck(self, tier):
        if tier == 1:
            if len(self._tier1_deck)!=0:
                new_card = self._tier1_deck.pop()
                self._tier1.append(new_card)
        elif tier == 2:
            if len(self._tier2_deck)!=0:
                new_card = self._tier2_deck.pop()
                self._tier2.append(new_card)
        elif tier == 3:
            if len(self._tier3_deck)!=0:
                new_card = self._tier3_deck.pop()
                self._tier3.append(new_card)
        else:
            raise ValueError

    """
    Helper function that removes and returns the top card ot a specified tier deck.
    """
    def reserve_from_deck(self, tier):
        if tier == 1:
            if len(self._tier1_deck)!= 0:
               new_card = self._tier1_deck.pop()
               return new_card
            else:
               return None
        elif tier == 2:
            if len(self._tier2_deck)!= 0:
                new_card = self._tier2_deck.pop()
                return new_card
            else:
                return None
        elif tier == 3:
            if len(self._tier3_deck)!= 0:
                new_card = self._tier3_deck.pop()
                return new_card
            else:
                return None
        else:
            raise ValueError

    """ 
    Removes a card from the cards available to purchase from a specific tier.

    tier:   Int. The tier from which the card should be removed.
            If tier = 1, remove from tier 1. If tier = 2, remove from tier 2. If tier = 3, 
            remove from tier 3. Otherwise the method raises ValueError.

    card:   Card object. The card that should be removed from the board. 

    """
    def remove_tier_card(self, tier, card):
        if tier == 1:
            del self._tier1[card]
        elif tier == 2:
            del self._tier2[card]
        elif tier == 3:
            del self._tier3[card]
        else:
            raise ValueError


    """
    Removes gems from the game's available gems.

    gem_lst:    list of ints representing the number of gems of each color to remove. The order of the list is
                [red, blue, green, white, black]. For example, [0, 1, 3, 0, 2] would representing removing
                0 red gems, 1 blue gem, 3 green gems, 0 white gems, and 2 black gems.
    """
    def remove_gems(self, gem_lst):
        self._available_gems.remove(Color.WHITE, gem_lst[0])
        self._available_gems.remove(Color.BLACK, gem_lst[1])
        self._available_gems.remove(Color.GREEN, gem_lst[2])
        self._available_gems.remove(Color.RED, gem_lst[3])
        self._available_gems.remove(Color.BLUE, gem_lst[4])

    
    """
    Adds gems to the game's available gems.

    gem_lst:    list of ints representing the number of gems of each color to add. The order of the list is
                [red, blue, green, white, black]. For example, [0, 1, 3, 0, 2] would representing adding
                0 red gems, 1 blue gem, 3 green gems, 0 white gems, and 2 black gems.
    """
    def add_gems(self, gem_lst):
        self._available_gems.add(Color.WHITE, gem_lst[0])
        self._available_gems.add(Color.BLACK, gem_lst[1])
        self._available_gems.add(Color.GREEN, gem_lst[2])
        self._available_gems.add(Color.RED, gem_lst[3])
        self._available_gems.add(Color.BLUE, gem_lst[4])

    """
    Removes the given noble from the game's available nobles.

    noble: GemDict object. The noble to be removed from the board.
    """
    def remove_noble(self, noble):
        self._nobles.remove(noble)
    
    """
    Returns the card for the tier and card index specified, or None if it DNE.
    """
    def getTierCard(self, tier, card):
        c = None
        if (tier == 1):
            c = self._tier1[card]
        elif (tier == 2):
            c = self._tier2[card]
        elif (tier == 3):
            c = self._tier3[card]
        return c
    
    """
    Decrements the game's total number of available gold gems by 1.
    """
    def decr_gold(self):
        self._gold -= 1

    """
    Increments the game's total number of available gold gems by 1.
    """
    def incr_gold(self):
        self._gold += 1
    
    """
    Returns True if the current player is discarding cards.
    """
    def get_discarding(self):
        return self._discarding
    
    """
    Sets _discarding to dis.
    """
    def set_discarding(self, dis):
        self._discarding = dis
    
    """
    Returns None if nobody has won; else, a player's name.
    """
    def get_firstWinner(self):
        return self._firstWinner
    
    """
    Sets _firstWinner to fw.
    """
    def set_firstWinner(self, fw):
        self._firstWinner = fw
    
    """
    Sets _winners to empty list of winners.
    """
    def reset_winners(self):
        self._winners = []
    
    """
    Returns list of winners.
    """
    def get_winners(self):
        return self._winners
    
    """
    Returns winners message.
    """
    def get_winners_text(self):
        text = ""
        if (len(self._winners) == 0):
            return "Nobody won... [1000 Turn Limit]"
        if (len(self._winners) == 1):
            text = "" + self._winners[0] + " Wins!"
        elif (len(self._winners) > 1):
            for w in self._winners[:-2]:
                text += w + ", "
            text += self._winners[-2] + " and " + self._winners[-1] + " Win!"
        else:
            return ""
        return text
    
    """
    Add w to _winners.
    """
    def add_winner(self, w):
        self._winners.append(w)

    """
    Adds a player to the game's player list.

    player:     Player object. The player to be added to the player list. The player is added to
                the end of the list (will have the last turn).
    """
    def add_player(self, player):
        self._players.append(player)
    
    def can_buy_card(self, t, c, r):
        card = None
        if (r):
            card = self._players[t].get_reserved()[c]
        else:
            if (t == 1):
                card = self._tier1[c]
            elif (t == 2):
                card = self._tier2[c]
            elif (t == 3):
                card = self._tier3[c]
        
        difference = 0
        player = self._current_player
        keys = card.get_cost().get_data()
        discounts = player.get_discounts().get_data()
        adjusted_cost = [0] * 5
        
        #Check if user has enough gems to buy card (adjusted with discounts)
        for color in keys:
            card_cost = max(keys[color] - discounts[color], 0)
            adjusted_cost[color.value] = card_cost
            if card_cost < 0:
                card_cost = 0
            player_cash = player.get_gems().get_data()[color]
            if card_cost > player_cash:
                difference += card_cost - player_cash
        if difference > player.get_gold():
            return False
        return True 
    
    def toList(self):
        p = []
        i = 0
        for pl in self._players:
            rsv = []
            k = 0
            for r in pl.get_reserved():
                res = [0] * 5
                res[r.get_color().value] = 1
                rsv += [r.get_points()] + res + r.get_cost().data_gui()
                k += 1
            for j in range(3-k):
                rsv += [0] * 11
            p += rsv + [22-pl.get_points()] + pl.get_colors() + pl.get_discounts().data_gui()
            i += 1
        for j in range(4-i):
            p += [0] * 45
        
        g = [self._gold] + self._available_gems.data_gui()
        
        td = [len(self._tier1_deck)] + [len(self._tier2_deck)] + [len(self._tier3_deck)]
        
        nb = []
        i = 0
        for n in self._nobles:
            nb += n.data_gui()
            i += 1
        for j in range(5-i):
            nb += [0] * 5
            
        t1 = []
        i = 0
        for t in self._tier1:
            res = [0] * 5
            res[t.get_color().value] = 1
            t1 += [t.get_points()] + res + t.get_cost().data_gui()
            i += 1
        for j in range(4-i):
            t1 += [0] * 11
        
        t2 = []
        i = 0
        for t in self._tier2:
            res = [0] * 5
            res[t.get_color().value] = 1
            t2 += [t.get_points()] + res + t.get_cost().data_gui()
            i += 1
        for j in range(4-i):
            t2 += [0] * 11
        
        t3 = []
        i = 0
        for t in self._tier3:
            res = [0] * 5
            res[t.get_color().value] = 1
            t3 += [t.get_points()] + res + t.get_cost().data_gui()
            i += 1
        for j in range(4-i):
            t3 += [0] * 11
        
        return (p + g + td + nb + t1 + t2 + t3)
        
    
    def incr_interactions(self):
        self._interactions += 1
    
    def get_interactions(self):
        return self._interactions
    
    def input_info(self, stepsLeft):
        pturn = [0] * 4
        pind = self.current_player_index()
        pturn[pind] = 1
        return (self.toList() + self.possible_moves(pind) +
            pturn + [stepsLeft])
    
    """
    Returns all the possible moves in this state.
    Indexes [0...4] for whether it's possible to take at least one of the gem.
    Indexes [5...9] for whether it's possible to take at two of the gem.
    Indexes [10...24] for whether a card can be reserved; R-to-L, Tier 1 -> 3.
    Indexes [25...27] for whether a reserved card can be bought.
    Indexes [28...39] for whether a tier card can be bought; Tier 1 -> 3.
    Indexes [40...45] for whether the player can discard one of their colors.
    """
    def possible_moves(self, cpind):
        
        gm = self.get_avail_gems().data_gui()
        cp = self.get_players()[cpind]
        
        canTake1 = [0] * 5
        canTake2 = [0] * 5
        canReserve = [0] * 15
        canBuy = [0] * 15
        canDiscard = [0] * 6
        if (not self.get_discarding()):
            canTake1 = list(map(lambda n : int(n>0), gm))
            
            canTake2 = list(map(lambda n : int(n>3), gm))
            
            if (len(cp.get_reserved()) < 3):
                canReserve[0] = int(len(self.get_tier1_deck()) > 0)
                canReserve[5] = int(len(self.get_tier2_deck()) > 0)
                canReserve[10] = int(len(self.get_tier3_deck()) > 0)
                for i in range(len(self.get_tier1())):
                    canReserve[i+1] = 1
                for i in range(len(self.get_tier2())):
                    canReserve[i+6] = 1
                for i in range(len(self.get_tier3())):
                    canReserve[i+11] = 1
                    
            for r in range(len(cp.get_reserved())):
                canBuy[r] = int(self.can_buy_card(cpind, r, True))
            for t1 in range(len(self.get_tier1())):
                canBuy[t1+3] = int(self.can_buy_card(1, t1, False))
            for t2 in range(len(self.get_tier2())):
                canBuy[t2+7] = int(self.can_buy_card(2, t2, False))
            for t3 in range(len(self.get_tier3())):
                canBuy[t3+11] = int(self.can_buy_card(3, t3, False))
        
        else:
            canDiscard = list(map(lambda n : int(n>0), cp.get_colors()))

        return (canTake1 + canTake2 + canReserve + canBuy + canDiscard)


"""
    A Card will contain:

    color: a Color indicating the discount the card gives
    points: an int indicating the number of points the card gives
    cost: A GemDict indicating the cost of the card
"""
class Card:
    """
    cost_lst: a list of the number of each color of gem that the card costs [red, blue, green, white, black]. 
    For example, [0, 1, 3, 0, 2] would representing the card costing 
    0 red gems, 1 blue gem, 3 green gems, 0 white gems, and 2 black gems.
    """
    def __init__(self, color, points, cost_lst, tier):
        self._color = color
        self._points = points
        self._cost = GemDict(cost_lst)
        self._tier = tier
        self._reserved = [False, None]

    """Returns the Color indicated the discount the card gives."""
    def get_color(self):
        return self._color

    """Returns the point value of the card."""
    def get_points(self):
        return self._points

    """Returns the cost of the card as a Gem Dict."""
    def get_cost(self):
        return self._cost
    
    """Returns the tier of the card. One of [1,2,3]."""
    def get_tier(self):
        return self._tier
    
    """Returns boolean for whether the card is reserved."""
    def reserved(self):
        return self._reserved
    
    """Returns [True, index], where index is the index in its reserve pile."""
    def reserve(self, index):
        self._reserved = [True, index]
    
    def __str__(self):
        return ( str(self._points) + "       " + str(self._color) +
            "\n\n\n" + "W|K|E|R|B\n" +
            str(self.get_cost()) )

"""
    A Player will contain:

    name: a string representing the name of the player. ex. HUMAN 0 for human player, AI 0 for AI player.
    discounts: A GemDict with Color keys and int values. Represents the number of cards of each color a player has.
    gems: A GemDict with with Color keys and int values. Represents the number of gems of each color a player has.
    gold: an int representing the number of gold gems a player has
    reserved: A list of Card objects that the player has reserved
    points: The number of points a player has
    player_type: A PlayerType indicating whether the player is AI or human
    num_cards: An int indicating the number of cards a player has bought (used for end-game tiebreaker).
    num_moves: Number of moves the player has taken
    gems_taken: list of gem colors in the order that the player took them (only used for AI)
"""
class Player:
    """
    Sets up an empty Player object with each of the attributes described above.
    """
    def __init__(self, player_type, name):
        self._name = name
        self._discounts = GemDict([0,0,0,0,0])
        self._gems = GemDict([0,0,0,0,0])
        self._gold = 0
        self._reserved = []
        self._points = 0
        self._player_type = player_type
        self._num_cards = 0
        self._num_moves = 0
        self._gems_taken = []
        self._move_dict = {'take_two' : 0, 'take_three' : 0, 'buy' : 0, 'buy_noble' : 0, 'reserve' : 0, 'reserve_top': 0, 'discard' : 0}

    
    def get_move_dict(self):
        return self._move_dict
        
    def add_move_dict(self, move):
        self._move_dict[move] += 1

    """
    Returns the type of this player.
    """
    def get_player_type(self):
        return self._player_type
        
    """
    Returns the name of the current player.
    """
    def get_name(self):
        return self._name

    """
    Returns the player's discounts as a GemDict which represents the number of cards of each color a player has.
    """
    def get_discounts(self):
        return self._discounts

    """
    Returns the number of gems of each color the player has.
    """
    def get_gems(self):
        return self._gems

    """
    Returns the number of gold gems a player has.
    """
    def get_gold(self):
        return self._gold

    """
    Returns a list of Card objects the player has reserved.
    """
    def get_reserved(self):
        return self._reserved

    """
    Returns the number of points the player has.
    """
    def get_points(self):
        return self._points

    """
    Returns number of cards the player has bought.
    """
    def get_purchased(self):
        return self._num_cards
    
    """
    Returns number of cards the player has bought.
    """
    def gemGoldAmt(self):
        return self._gems.total_gems() + self._gold
    
    """
    Returns the list of all the colors the player owns.
    """
    def get_colors(self):
        return [self._gold] + self._gems.data_gui()

    """
    Increments the player's number of gold gems by 1.
    """
    def incr_gold(self):
        self._gold += 1

    """
    Decrements the player's number of gold gems by 1.
    """
    def decr_gold(self):
        self._gold -= 1

    """
    Adds card to the player's list of reserved cards.
    """
    def add_reserved(self, card):
        self._reserved.append(card)
        card.reserve(self._reserved.index(card))

    """
    Removes card from the player's list of reserved cards.
    """
    def remove_reserved(self, card):
        del self._reserved[card]

    """
    Adds the color to the player's discounts.
    """
    def set_discount(self, color):
        self._discounts.add(color, 1)

    """
    Adds the given number of gems in color_lst to the player's total gems. color_lst is a list
    of ints representing the number of gems of each color to be added. The order of color_lst is 
    [red, blue, green, white, black]. For example, [0, 1, 3, 0, 2] would representing adding
    0 red gems, 1 blue gem, 3 green gems, 0 white gems, and 2 black gems.
    """
    def add_gems(self, color_lst):
        self._gems.add(Color.WHITE, color_lst[0])
        self._gems.add(Color.BLACK, color_lst[1])
        self._gems.add(Color.GREEN, color_lst[2])
        self._gems.add(Color.RED, color_lst[3])
        self._gems.add(Color.BLUE, color_lst[4])

    """
    Removes the given number of gems in color_lst from the player's total gems. color_lst is a list
    of ints representing the number of gems of each color to be added. The order of color_lst is 
    [red, blue, green, white, black]. For example, [0, 1, 3, 0, 2] would representing removing
    0 red gems, 1 blue gem, 3 green gems, 0 white gems, and 2 black gems.
    """
    def remove_gems(self, color_lst):
        self._gems.remove(Color.WHITE, color_lst[0])
        self._gems.remove(Color.BLACK, color_lst[1])
        self._gems.remove(Color.GREEN, color_lst[2])
        self._gems.remove(Color.RED, color_lst[3])
        self._gems.remove(Color.BLUE, color_lst[4])

    def ai_remove_gems(self, color_lst):
        if self._player_type == 2: #use only for AI
            for i in range(len(color_lst)):
                for j in range(color_lst[i]):
                    if i == 0:
                        self._gems_taken.remove(Color.WHITE)
                    elif i == 1:
                        self._gems_taken.remove(Color.BLACK)
                    elif i == 2:
                        self._gems_taken.remove(Color.GREEN)
                    elif i == 3:
                        self._gems_taken.remove(Color.RED)
                    elif i == 4:
                        self._gems_taken.remove(Color.BLUE)

    """
    Returns list of gems that the player took in the order they took them
    """
    def get_gems_ordered(self):
        return self._gems_taken

    """
    Takes a list of Colors and adds them to the front of the list of gems that have 
    already been taken
    """
    def ai_add_gems(self, color_lst):
        color_lst + self._gems_taken

    """
    Adds the given number of points to the player's point total.
    """
    def set_points(self, num_points):
        self._points += num_points

    """
    Increments the player's number of purchased cards by 1.
    """
    def incr_card_total(self):
        self._num_cards += 1
        
    """
    Returns the player's number of moves so far, not including this current one. 
    """
    def get_num_moves(self):
        return self._num_moves
    
    """
    Increments the player's number of moves by 1.
    """
    def incr_num_moves(self):
        self._num_moves += 1
    
    
    def __str__(self):
        gd = self._gold
        gm = self._gems
        dc = self._discounts
        return (
            str(self._points) + "               " + self._name + "\n\n\n" +
            "          G   " + "W|K|E|R|B\n" +
            "GEMS      " + str(gd) + "   " + str(gm) + "\n" +
            "CARDS         " + str(dc) + "\n" +
            "_______________________\n" + 
            "TOTAL     " + str(gd) + "   " + gm.addGD(dc)
        )
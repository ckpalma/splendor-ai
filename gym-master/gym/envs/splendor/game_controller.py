from gym.envs.splendor.structure import *
import os
import copy
import numpy as np
import tensorflow as tf
import csv
import random
from datetime import datetime
import joblib
from baselines.common.tf_util import get_session

random.seed(None)

def setSeed(s):
    random.seed(s)

"""
One of the move classes. Contains the necessary info and methods for when a player takes two gems of the same color.
"""
class TakeTwoMove():

    def __init__(self, color):
        self._color = color

    def get_color(self):
        return self._color

    def __eq__(self, other):
        """Override the default Equals behavior"""
        return self._color == other._color

"""
One of the move classes. Contains the necessary info and methods for when a player takes three gems of different colors.
Also should be used if a player cannot take 3 gems because there are fewer than 3 colors remaining.
"""
class TakeThreeMove():

    def __init__(self, color1, color2, color3):
        self._color1 = color1
        self._color2 = color2
        self._color3 = color3

    def __eq__(self, other):
        """Override the default Equals behavior"""
        return self._color1 == other._color1 and self._color2 == other._color2 and self._color3 == other._color3

    def get_colors(self):
        return [self._color1, self._color2, self._color3]


"""
One of the move classes. Contains the necessary info and methods for when a player buys a card.
"""
class Buy():
    def __init__(self, tier, card, reserved):
        self._card = card
        self._tier = tier
        self._reserved = reserved

    def get_card(self):
        return self._card
    
    def get_tier(self):
        return self._tier
    
    def get_reserved(self):
        return self._reserved
    
    def __eq__(self, other):
        """Override the default Equals behavior"""
        return self._tier == other._tier and self._card == other._card and self._reserved == other._reserved

"""
One of the move classes. Contains the necessary info and methods for when a player buys a noble card.
"""
class Buy_Noble():
    def __init__(self, noble):
        self._noble = noble

    def get_noble(self):
        return self._noble

"""
One of the move classes. Contains the necessary info and methods for when a player takes reserves a card.
"""
class Reserve():
    def __init__(self, tier, card):
        self._tier = tier
        self._card = card

    def get_tier(self):
        return self._tier    
    
    def get_card(self):
        return self._card

"""
One of the move classes. Contains the necessary info and methods for when a player takes reserves a card from the top
of a deck.
"""
class Reserve_Top():
    def __init__(self, tier):
        self._tier = tier

    def get_tier(self):
        return self._tier

"""
One of the move classes. Contains the necessary info and methods for when a player discards gems.
"""
class Discard():

    def __init__(self, color):
        self._color = color

    def __eq__(self, other):
        """Override the default Equals behavior"""
        return self._color == other._color

    def get_color(self):
        return self._color

"""
    The current_player buys the specified card. Returns the new state if the card can be bought by current_player,
    otherwise returns None.
"""
def buy_card(state, t, c, r):
    card = None
    if (r):
        card = state.get_players()[t].get_reserved()[c]
    else:
        if (t == 1):
            card = state.get_tier1()[c]
        elif (t == 2):
            card = state.get_tier2()[c]
        elif (t == 3):
            card = state.get_tier3()[c]
    
    difference = 0
    player = state.get_current_player()
    keys = card.get_cost().get_data()
    discounts = player.get_discounts().get_data()
    adjusted_cost = [0] * 5
    
    #Check if user has enough gems to buy card (adjusted with discounts)
    for color in keys:
        card_cost = max(card.get_cost().get_data()[color] - discounts[color],0)
        adjusted_cost[color.value] = card_cost
        if card_cost < 0:
            card_cost = 0
        player_cash = player.get_gems().get_data()[color]
        if card_cost > player_cash:
            difference += card_cost - player_cash
    if difference > player.get_gold():
        return None 
    #Able to buy the card, deduct/add to the relevant fields in player
    for color in keys:
        cost = adjusted_cost[color.value]
        diff = cost - player.get_gems().get_data()[color]
        #Need to use gold gems to buy card
        if diff > 0:
            for gem in range(diff):
                player.decr_gold()
                state.incr_gold()
                adjusted_cost[color.value] = adjusted_cost[color.value] - 1
    if (card.reserved()[0]):
        player.remove_reserved(card.reserved()[1])
    else:
        state.remove_tier_card(t, c)
        state.draw_from_deck(t)
    player.remove_gems(adjusted_cost)
    state.add_gems(adjusted_cost)
    player.incr_card_total()
    player.set_points(card.get_points())
    player.set_discount(card.get_color())
    return state 

"""
    The current_player takes three gems of the specified colors. Returns new state if the move is possible, otherwise
    returns None. color1, color2, color3 are Color objects but can be None if the player can only take 2 or 1 gem.
    Assumes that if the player only takes 2 or 1 gem, they must be different colors and not taking 2 gems of the same color. 
"""
def take_three_gems(state, color1, color2, color3):
    colors = []
    if color1 != None:
        colors.append(color1)
    if color2 != None:
        colors.append(color2)
    if color3 != None:
        colors.append(color3)
        
    #Check if move is possible
    for c in colors:
        if colors.count(c) > 1:
            return None
            
    
            
    # Move possible
    colors_count = [0] * 5
    for c in colors:
        if state.get_avail_gems().get_data()[c] == 0:
            return None 
        else:
            colors_count[c.value] = colors_count[c.value] + 1
    # modify state: remove gems from state and add to player.
    state.remove_gems(colors_count)
    state.get_current_player().add_gems(colors_count)
    return state 

"""
    The current_player takes two gems of the specified color. Returns new state if the move is possible, otherwise
    returns None.
"""
def take_two_gems(state, color):
    #check if there's at least 4 gems of that color left in state
    num_gems = state.get_avail_gems().get_data()[color]
    if num_gems < 4:
        return None
    #move is possible
    else:
        colors_count = [0] * 5
        colors_count[color.value] = 2
        state.remove_gems(colors_count)
        state.get_current_player().add_gems(colors_count)
        return state

"""
    The current_player reserves the specified card and receives one gold gem. Returns new state if the move is possible, 
    otherwise returns None.
    Precondition: card is a valid card on board (-or is the topmost card in one of the 3 decks-).
"""
def reserve_card(state, tier, card):
    # if player has 3 reserved cards already, cannot reserve any more
    if len(state.get_current_player().get_reserved()) == 3:
        return None
    #remove this card from state. Tier = -1 means the card was drawn from the deck and therefore does not need to be
    #removed from tiers
    c = None
    if (tier == 1):
        c = state.get_tier1()[card]
    elif (tier == 2):
        c = state.get_tier2()[card]
    elif (tier == 3):
        c = state.get_tier3()[card]
    if tier > 0:
        state.remove_tier_card(tier, card)
        state.draw_from_deck(tier)
        state.get_current_player().add_reserved(c)
        if state.get_num_gold() > 0:
            state.get_current_player().incr_gold()
            state.decr_gold()
    return state 

"""
    The current_player reserved the top card of the specified tier. Returns new state if the move is possible, otherwise
    returns None.
"""
def reserve_top(state, tier):
    if len(state.get_current_player().get_reserved()) == 3:
        return None

    card = state.reserve_from_deck(tier)
    if card == None:
        return None

    state.get_current_player().add_reserved(card)
    if state.get_num_gold() > 0:
        state.get_current_player().incr_gold()
        state.decr_gold()
    return state

"""
    Returns a list of nobles the current_player is eligible to take, or None if the player cannot take any.
"""
def check_nobles(state):
    current_player = state.get_current_player()
    possible_noble_list = []
    for noble in state.get_nobles():
        if (current_player.get_discounts()[Color.RED] >= noble[Color.RED] and
            current_player.get_discounts()[Color.BLUE] >= noble[Color.BLUE] and
            current_player.get_discounts()[Color.BLACK] >= noble[Color.BLACK] and
            current_player.get_discounts()[Color.WHITE] >= noble[Color.WHITE] and
            current_player.get_discounts()[Color.GREEN] >= noble[Color.GREEN]):
            possible_noble_list.append(noble)
    if possible_noble_list == []:
        return None
    else:
        return possible_noble_list

"""
    The current_player discards the specified gem. Returns the new state.
"""
def discard(state, color):
    player = state.get_current_player()
    if color == "G":
        if player.get_gold() == 0:
            return None
        player.decr_gold()
        state.incr_gold()
    elif color == "R":
        if player.get_gems().get_data()[Color.RED] == 0:
            return None
        dList = [1, 0, 0, 0 ,0]
        player.remove_gems(dList)
        state.add_gems(dList)
    elif color == "B":
        if player.get_gems().get_data()[Color.BLUE] == 0:
            return None
        dList = [0, 1, 0, 0 ,0]
        player.remove_gems(dList)
        state.add_gems(dList)
    elif color == "E":
        if player.get_gems().get_data()[Color.GREEN] == 0:
            return None
        dList = [0, 0, 1, 0 ,0]
        player.remove_gems(dList)
        state.add_gems(dList)
    elif color == "W":
        if player.get_gems().get_data()[Color.WHITE] == 0:
            return None
        dList = [0, 0, 0, 1 ,0]
        player.remove_gems(dList)
        state.add_gems(dList)
    elif color == "K":
        if player.get_gems().get_data()[Color.BLACK] == 0:
            return None
        dList = [0, 0, 0, 0 ,1]
        player.remove_gems(dList)
        state.add_gems(dList)

    return state

def gemDictMap(gDict, gem):
    data = gDict.get_data()
    if (gem == 1):
        return data[Color.WHITE]
    elif (gem == 2):
        return data[Color.BLACK]
    elif (gem == 3):
        return data[Color.GREEN]
    elif (gem == 4):
        return data[Color.RED]
    elif (gem == 5):
        return data[Color.BLUE]

def buy_noble(state, noble):
    gems = state.get_current_player().get_discounts()
    nob = state.get_nobles()[noble]
    if (gemDictMap(gems,1) < gemDictMap(nob,1) or
        gemDictMap(gems,2) < gemDictMap(nob,2) or
        gemDictMap(gems,3) < gemDictMap(nob,3) or
        gemDictMap(gems,4) < gemDictMap(nob,4) or
        gemDictMap(gems,5) < gemDictMap(nob,5)):
        return None
    state.get_current_player().set_points(3)
    del state.get_nobles()[noble]
    return state


"""
    The current_player makes the specified move. Returns the new state if the move is possible, otherwise returns None.
"""
def play(state, move):
    if isinstance(move, TakeTwoMove):
        return take_two_gems(state, move.get_color())
    elif isinstance(move, TakeThreeMove):
        return take_three_gems(state, move.get_colors()[0], move.get_colors()[1], move.get_colors()[2])
    elif isinstance(move, Buy):
        return buy_card(state, move.get_tier(), move.get_card(), move.get_reserved())
    elif isinstance(move, Buy_Noble):
        return buy_noble(state, move.get_noble())
    elif isinstance(move, Reserve):
        return reserve_card(state, move.get_tier(), move.get_card())
    elif isinstance(move, Reserve_Top):
        return reserve_top(state, move.get_tier())
    elif isinstance(move, Discard):
        return discard(state, move.get_color())
    else:
        raise ValueError

################################# NEW AI #####################################

"""
Returns the remaining cost of a card as a GemDict. Useful for creating priority lists
"""
def remaining_cost(state, card):
    curr_player = state.get_current_player()
    curr_gems = curr_player.get_gems()
    discounts = curr_player.get_discounts()
    gold = curr_player.get_gold()
    rem_cost = [0] * 5
    for key, value in card.get_cost().get_data().items():
        cost = value - curr_gems.get_data()[key] - discounts.get_data()[key]
        if cost > 0 and gold > cost:
            cost = 0
            gold -= cost
        elif cost > 0 and gold <= cost:
            cost -= gold
            gold -= cost
        rem_cost[key.value - 1] = cost
    return GemDict(rem_cost) 

"""
Returns the sum of all values in a GemDict as an int. Useful for calculating things like total remaining cost of a card.
"""
def sum_gem_dict(gem_dict):
    sum = 0
    for value in gem_dict.get_data().values():
        sum += value
    return sum
        


"""Returns a list of Colors, ordered by the total presence of that color in costs of all cards in play. Most dominant
"""
def determine_dominant_colors(state):
    cards = state.get_tier1_deck() + state.get_tier2_deck() + state.get_tier3_deck()
    presence = dict() #unsorted
    for color in Color:
        if color != Color.GOLD: 
            presence[color] = 0
        
    for card in cards:
        for color in Color:
            if(color != Color.GOLD): 
                presence[color] += card.get_cost().get_data()[color]
            
    return (sorted(presence, key=lambda color: presence[color]))
    

def check_feasible(state, card):
    current = state.get_current_player()
    gems = current.get_gems().get_data()
    available = state.get_avail_gems().get_data()
    cost = remaining_cost(state, card).get_data()
    cost_for_checking_ten = cost.copy()
    cost_for_checking_ten[Color.RED] += gems[Color.RED]
    cost_for_checking_ten[Color.BLUE] += gems[Color.BLUE]
    cost_for_checking_ten[Color.GREEN] += gems[Color.GREEN]
    cost_for_checking_ten[Color.WHITE] += gems[Color.WHITE]
    cost_for_checking_ten[Color.BLACK] += gems[Color.BLACK]


    cost[Color.RED] -= available[Color.RED]
    cost[Color.BLUE] -= available[Color.BLUE]
    cost[Color.GREEN] -= available[Color.GREEN]
    cost[Color.WHITE] -= available[Color.WHITE]
    cost[Color.BLACK] -= available[Color.BLACK]



    total = sum_gem_dict(GemDict([cost[Color.RED], cost[Color.BLUE], cost[Color.GREEN], cost[Color.WHITE], cost[Color.BLACK]]))
    total_for_checking_ten = sum_gem_dict(GemDict([cost_for_checking_ten[Color.RED], cost_for_checking_ten[Color.BLUE], cost_for_checking_ten[Color.GREEN], cost_for_checking_ten[Color.WHITE], cost_for_checking_ten[Color.BLACK]]))

    if total <= 0 and total_for_checking_ten <= 10:
        return True
    else:
        return False


"""
Returns a list of feasible Tier 1 cards, ordered first by color ranking given by determine_dominant_colors, then by
lowest remaining cost (highest first for both). Ignore points.

Definition of "feasible": The AI can buy the card with it's current gems and discounts, and any gems available in the
supply. Any card that costs more than 10 gems (taking into account discounts) should also immediately be considered not
feasible.
"""
def determine_feasible_tier_1(state):
    tier1 = state.get_tier1()
    dominant_colors = determine_dominant_colors(state)
    priority1_feasible = []
    priority2_feasible = []
    priority3_feasible = []
    priority4_feasible = []
    priority5_feasible = []

    for card in tier1:
        if check_feasible(state, card):
            if card.get_color() == dominant_colors[0]:
                priority1_feasible.append(card)
            elif card.get_color() == dominant_colors[1]:
                priority2_feasible.append(card)
            elif card.get_color() == dominant_colors[2]:
                priority3_feasible.append(card)
            elif card.get_color() == dominant_colors[3]:
                priority4_feasible.append(card)
            elif card.get_color() == dominant_colors[4]:
                priority5_feasible.append(card)

    sorted_priority1 = sorted(priority1_feasible, key=lambda card: sum_gem_dict(remaining_cost(state, card)))
    sorted_priority1.reverse()
    sorted_priority2 = sorted(priority2_feasible, key=lambda card: sum_gem_dict(remaining_cost(state, card)))
    sorted_priority2.reverse()
    sorted_priority3 = sorted(priority3_feasible, key=lambda card: sum_gem_dict(remaining_cost(state, card)))
    sorted_priority3.reverse()
    sorted_priority4 = sorted(priority4_feasible, key=lambda card: sum_gem_dict(remaining_cost(state, card)))
    sorted_priority4.reverse()
    sorted_priority5 = sorted(priority5_feasible, key=lambda card: sum_gem_dict(remaining_cost(state, card)))
    sorted_priority5.reverse()

    return sorted_priority1 + sorted_priority2 + sorted_priority3 + sorted_priority4 + sorted_priority5

"""
Returns a list of colors, in order of what gems are needed most. Scroll through the list of ranked feasible cards in order 
to determine this. The gems it needs the most of to buy the highest priority card come first. An AI should never
take two of the same gem--the list this function returns should be all colors, ranked from most needed to least.
Break ties however you see fit.

Ex. If remaining cost of a card is 3 red, 2 green, and 1 blue, 1 black gem_list should be red, green, blue, black, white
"""
def gem_priority_list(state, card_list):
    gems_needed = GemDict([0,0,0,0,0]) #[red, blue, green, white black]
    for card in range(len(card_list)):
        gems_left = remaining_cost(state, card_list[card]) #gems needed to buy this card
        gems_needed.add(Color.RED, gems_left.get_data()[Color.RED] * 1/(card+1)) #weight by its rank in the list
        gems_needed.add(Color.GREEN, gems_left.get_data()[Color.GREEN] * 1/(card + 1))
        gems_needed.add(Color.BLUE, gems_left.get_data()[Color.BLUE] * 1/(card + 1))
        gems_needed.add(Color.BLACK, gems_left.get_data()[Color.BLACK] * 1/(card + 1))
        gems_needed.add(Color.WHITE, gems_left.get_data()[Color.WHITE] * 1/(card + 1))

    gems_needed_lst = list(gems_needed.get_data().items())
    gems_needed_lst.sort(key=lambda x: x[1])
    gems_needed_lst.reverse()
    color_rank = []
    for t in gems_needed_lst:
        color_rank.append(t[0])
    return color_rank

"""
Should be called when the AI has 8, 9, or 10 gems. Returns the first card in card_list (the priority list of cards) that
the AI can currently buy. Returns None if it can't buy any.
"""
def buy_with_too_many_gems(state, card_list):
    ai_gems = state.get_current_player().get_gems().get_data()
    ai_gold = state.get_current_player().get_gold()
    for card in range(len(card_list)):
        can_buy = True
        gold_left = ai_gold
        card_cost = card_list[card].get_cost().get_data()
        for color, num in card_cost.items():
            if ai_gems[color] >= num: #if the ai has enough gems of this color
                can_buy = can_buy and True
            elif ai_gems[color] + gold_left >= num: #if the ai has enough gems of this color plus some gold
                can_buy = can_buy and True
                gold_left = ai_gems[color] + gold_left - num
            else: #ai doesnt have enough gems of this color
                can_buy = can_buy and False
        if can_buy == True:
            return card_list[card]
    return None

"""
Returns a Discard object of the oldest color an AI took
"""
def determine_discard(state):
    for key, val in state.get_current_player().get_gems().get_data().items():
        if val > 0:
            return key
    
    # ai_gems_taken = state.get_current_player().get_gems_ordered()
    # the_discard = Discard(ai_gems_taken[-1])
    # state.get_current_player().ai_remove_gems([ai_gems_taken[-1]])
    # return the_discard

"""
Return the move (use one of the move objects) the AI should make, using the following instructions:
1. Determine the dominant colors on the board
2. Determine a list of feasible tier 1 cards
3. Determine a gem priority list based on that
4. If AI is at 8, 9, or 10 gems, determine card to buy using buy_with_too_many_gems
4.5 If that returns None, use gem_priority list. If gem_priority_list is empty, pass. An AI should never take two of 
the same gem. Keep in mind in some edge cases, this means the AI will only take two seperate gems.
5. If AI is at 7 or less gems, try to buy top priority card from tier 1. If it can't, take gems listed in gem_priority_list.
6. If there are no valid moves (it can't buy cards and can't take gems), pass.
"""
def determine_early_move(state):
    total_ai_gems = state.get_current_player().get_gems().total_gems()
    feas_cards = []
    card_to_buy = None

    if (8 <= total_ai_gems and total_ai_gems <= 10):
        feas_cards = determine_feasible_all(state)
        card_to_buy = buy_with_too_many_gems(state, feas_cards)

    else:
        feas_cards = determine_feasible_tier_1(state)
        if feas_cards != []:
            rem_cost = sum_gem_dict(remaining_cost(state, feas_cards[0]))
            if rem_cost == 0:
                card_to_buy = feas_cards[0]
            else:
                card_to_buy = None
        else:
            card_to_buy = None

    if card_to_buy == None:
        gem_priority = gem_priority_list(state, feas_cards)

        if gem_priority == []:
            return None 
        else:
            #take gems
            colors_to_take = []
            play_gems = state.get_avail_gems().get_data()
            for color in gem_priority:
                #can only take gems if there will be 4 left after the gem is taken
                if (play_gems[color] != 0): 
                    colors_to_take.append(color)
            state.get_current_player().ai_add_gems(colors_to_take)
            if len(colors_to_take) >= 3:
                return TakeThreeMove(colors_to_take[0], colors_to_take[1], colors_to_take[2])
            elif len(colors_to_take) == 2:
                return TakeThreeMove(colors_to_take[0], colors_to_take[1], None)
            elif len(colors_to_take) == 1:
                return TakeThreeMove(colors_to_take[0], None, None)
    else:
        tier = card_to_buy.get_tier()
        int_card = 0
        if tier == 1:
            tier_1_deck = state.get_tier1()
            for card in range(len(tier_1_deck)):
                for key, val in tier_1_deck[card].get_cost().get_data().items():
                    if (val != card_to_buy.get_cost().get_data()[key]):
                        return None
                int_card = card
        elif tier == 2:
            tier_2_deck = state.get_tier2()
            for card in range(len(tier_2_deck)):
                for key, val in tier_2_deck[card].get_cost().get_data().items():
                    if (val != card_to_buy.get_cost().get_data()[key]):
                        return None
                int_card = card
        elif tier == 3:
            tier_3_deck = state.get_tier3()
            for card in range(len(tier_3_deck)):
                for key, val in tier_3_deck[card].get_cost().get_data().items():
                    if (val != card_to_buy.get_cost().get_data()[key]):
                        return None
                int_card = card
        return Buy(card_to_buy.get_tier(), int_card, False)

    return None #returning none for passing



"""
Same as determine_feasible_tier_1, but order all cards instead of Tier 1. Order using highest points first, then lowest
remaining cost first. Don't use dominant colors here.
"""
def determine_feasible_all(state):
    tier_all = state.get_tier1() + state.get_tier2() + state.get_tier3()
    dominant_colors = determine_dominant_colors(state)
    priority1_feasible = []
    priority2_feasible = []
    priority3_feasible = []
    priority4_feasible = []
    priority5_feasible = []
    priority6_feasible = []

    for card in tier_all:
        if check_feasible(state, card):
            if card.get_points() == 5:
                priority1_feasible.append(card)
            elif card.get_points() == 4:
                priority2_feasible.append(card)
            elif card.get_points() == 3:
                priority3_feasible.append(card)
            elif card.get_points() == 2:
                priority4_feasible.append(card)
            elif card.get_points() == 1:
                priority5_feasible.append(card)
            elif card.get_points() == 0:
                priority6_feasible.append(card)

    sorted_priority1 = sorted(priority1_feasible, key=lambda card: sum_gem_dict(remaining_cost(state, card)))
    sorted_priority2 = sorted(priority2_feasible, key=lambda card: sum_gem_dict(remaining_cost(state, card)))
    sorted_priority3 = sorted(priority3_feasible, key=lambda card: sum_gem_dict(remaining_cost(state, card)))
    sorted_priority4 = sorted(priority4_feasible, key=lambda card: sum_gem_dict(remaining_cost(state, card)))
    sorted_priority5 = sorted(priority5_feasible, key=lambda card: sum_gem_dict(remaining_cost(state, card)))
    sorted_priority6 = sorted(priority6_feasible, key=lambda card: sum_gem_dict(remaining_cost(state, card)))

    return sorted_priority1 + sorted_priority2 + sorted_priority3 + sorted_priority4 + sorted_priority5 + sorted_priority6

"""
Same as determine_early_move, but don't use dominant colors and use determine_feasible_all to get the card priority list
instead of just using tier 1.
"""
def determine_late_move(state):
    total_ai_gems = state.get_current_player().get_gems().total_gems()
    feas_cards = determine_feasible_all(state)
    for i in feas_cards:
        if total_ai_gems >= 8 and total_ai_gems <= 10:
            card_to_buy = buy_with_too_many_gems(state, feas_cards)
        else:
            if feas_cards != []:
                rem_cost = sum_gem_dict(remaining_cost(state, feas_cards[0]))
                if rem_cost == 0:
                    card_to_buy = feas_cards[0]
                else:
                    card_to_buy = None
            else:
                card_to_buy = None


    if card_to_buy == None:
        gem_priority = gem_priority_list(state, feas_cards)

        if gem_priority == []:
            return None
        else:
            #take gems
            colors_to_take = []
            play_gems = state.get_avail_gems().get_data()
            for color in gem_priority:
                #can only take gems if there will be 4 left after the gem is taken
                if (play_gems[color] != 0):
                    colors_to_take.append(color)
            state.get_current_player().ai_add_gems(colors_to_take)
            if len(colors_to_take) >= 3:
                return TakeThreeMove(colors_to_take[0], colors_to_take[1], colors_to_take[2])
            elif len(colors_to_take) == 2:
                return TakeThreeMove(colors_to_take[0], colors_to_take[1], None)
            elif len(colors_to_take) == 1:
                return TakeThreeMove(colors_to_take[0], None, None)
    else:
        tier = card_to_buy.get_tier()
        int_card = 0
        if tier == 1:
            tier_1_deck = state.get_tier1()
            for card in range(len(tier_1_deck)):
                for key, val in tier_1_deck[card].get_cost().get_data().items():
                    if (val != card_to_buy.get_cost().get_data()[key]):
                        return None
                int_card = card
        elif tier == 2:
            tier_2_deck = state.get_tier2()
            for card in range(len(tier_2_deck)):
                for key, val in tier_2_deck[card].get_cost().get_data().items():
                    if (val != card_to_buy.get_cost().get_data()[key]):
                        return None
                int_card = card
        elif tier == 3:
            tier_3_deck = state.get_tier3()
            for card in range(len(tier_3_deck)):
                for key, val in tier_3_deck[card].get_cost().get_data().items():
                    if (val != card_to_buy.get_cost().get_data()[key]):
                        return None
                int_card = card
        return Buy(card_to_buy.get_tier(), int_card, False)
    return None

"""
Adds the given move to the dictionary that keeps track of the ai's moves
"""
def store_move(state, move):
    ai = state.get_current_player()
    if isinstance(move, TakeTwoMove):
        ai.add_move_dict('take_two')
    elif isinstance(move, TakeThreeMove):
        ai.add_move_dict('take_three')
    elif isinstance(move, Buy):
        ai.add_move_dict('buy')
    elif isinstance(move, Buy_Noble):
        ai.add_move_dict('buy_noble')
    elif isinstance(move, Reserve):
        ai.add_move_dict('reserve')
    elif isinstance(move, Reserve_Top):
        ai.add_move_dict('reserve_top')
    elif isinstance(move, Discard):
        ai.add_move_dict('discard')
    else:
        raise ValueError


"""
Writes ai move data to file
"""
def write_moves_to_csv(state):
    name = state.get_current_player().get_name()
    moves_dict = state.get_current_player().get_move_dict()
    file_exists = os.path.isfile('{} moves.csv'.format(name))
    with open('{} moves.csv'.format(name), 'a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[field for field in moves_dict])
        if not file_exists:
            writer.writeheader()
        writer.writerow(moves_dict)

"""
Writes ai move data to file
"""
def write_moves(state, csv=False):
    if csv:
        write_moves_to_csv(state)
    else:
        name = state.get_current_player().get_name()
        moves_dict = state.get_current_player().get_move_dict()
        f = open("{} moves.txt".format(name), 'a')
        f.write("take three : {}, take two : {}, buy : {}, buy_noble : {}, reserve : {}, reserve top : {}, discard : {}\n".
            format(moves_dict['take_three'], moves_dict['take_two'], moves_dict['buy'], moves_dict['buy_noble'],
                moves_dict['reserve'], moves_dict['reserve_top'], moves_dict['discard']))

def standardize_move(move):
    if isinstance(move, TakeThreeMove):
        data = move.get_colors()
        if Color.WHITE in data and Color.BLACK in data and Color.GREEN in data:
            return TakeThreeMove(Color.WHITE, Color.BLACK, Color.GREEN)
        elif Color.WHITE in data and Color.BLACK in data and Color.RED in data:
            return TakeThreeMove(Color.WHITE, Color.BLACK, Color.RED)
        elif Color.WHITE in data and Color.BLACK in data and Color.BLUE in data:
            return TakeThreeMove(Color.WHITE, Color.BLACK, Color.BLUE)
        elif Color.WHITE in data and Color.GREEN in data and Color.RED in data:
            return TakeThreeMove(Color.WHITE, Color.GREEN, Color.RED)
        elif Color.WHITE in data and Color.GREEN in data and Color.BLUE in data:
            return TakeThreeMove(Color.WHITE, Color.GREEN, Color.BLUE)
        elif Color.WHITE in data and Color.RED in data and Color.BLUE in data:
            return TakeThreeMove(Color.WHITE, Color.RED, Color.BLUE)
        elif Color.BLACK in data and Color.GREEN in data and Color.RED in data:
            return TakeThreeMove(Color.BLACK, Color.GREEN, Color.RED)
        elif Color.BLACK in data and Color.GREEN in data and Color.BLUE in data:
            return TakeThreeMove(Color.BLACK, Color.GREEN, Color.BLUE)
        elif Color.BLACK in data and Color.RED in data and Color.BLUE in data:
            return TakeThreeMove(Color.BLACK, Color.RED, Color.BLUE)
        elif Color.GREEN in data and Color.RED in data and Color.BLUE in data:
            return TakeThreeMove(Color.GREEN, Color.RED, Color.BLUE)
        elif Color.WHITE in data and Color.BLACK in data:
            return TakeThreeMove(Color.WHITE, Color.BLACK, None)
        elif Color.WHITE in data and Color.GREEN in data:
            return TakeThreeMove(Color.WHITE, Color.GREEN, None)
        elif Color.WHITE in data and Color.RED in data:
            return TakeThreeMove(Color.WHITE, Color.RED, None)
        elif Color.WHITE in data and Color.BLUE in data:
            return TakeThreeMove(Color.WHITE, Color.BLUE, None)
        elif Color.BLACK in data and Color.GREEN in data:
            return TakeThreeMove(Color.BLACK, Color.GREEN, None)
        elif Color.BLACK in data and Color.RED in data:
            return TakeThreeMove(Color.WHITE, Color.GREEN, None)
        elif Color.BLACK in data and Color.BLUE in data:
            return TakeThreeMove(Color.WHITE, Color.GREEN, None)
        elif Color.GREEN in data and Color.RED in data:
            return TakeThreeMove(Color.GREEN, Color.RED, None)
        elif Color.GREEN in data and Color.BLUE in data:
            return TakeThreeMove(Color.GREEN, Color.BLUE, None)
        elif Color.RED in data and Color.BLUE in data:
            return TakeThreeMove(Color.RED, Color.BLUE, None)
        elif Color.WHITE in data:
            return TakeThreeMove(Color.WHITE, None, None)
        elif Color.BLACK in data:
            return TakeThreeMove(Color.BLACK, None, None)
        elif Color.GREEN in data:
            return TakeThreeMove(Color.GREEN, None, None)
        elif Color.RED in data:
            return TakeThreeMove(Color.RED, None, None)
        elif Color.BLUE in data:
            return TakeThreeMove(Color.BLUE, None, None)
    return move

def convert_move(state, move):
    output = ""
    cpind = state.current_player_index()
    if isinstance(move, TakeThreeMove):
        if move == TakeThreeMove(Color.WHITE, Color.BLACK, Color.GREEN):
            output = "t3wke"
        elif move == TakeThreeMove(Color.WHITE, Color.BLACK, Color.RED):
            output = "t3wkr"
        elif move == TakeThreeMove(Color.WHITE, Color.BLACK, Color.BLUE):
            output = "t3wkb"
        elif move == TakeThreeMove(Color.WHITE, Color.GREEN, Color.RED):
            output = "t3wer"
        elif move == TakeThreeMove(Color.WHITE, Color.GREEN, Color.BLUE):
            output = "t3web"
        elif move == TakeThreeMove(Color.WHITE, Color.RED, Color.BLUE):
            output = "t3wrb"
        elif move == TakeThreeMove(Color.BLACK, Color.GREEN, Color.RED): #
            output = "t3ker"
        elif move == TakeThreeMove(Color.BLACK, Color.GREEN, Color.BLUE): #
            output ="t3keb"
        elif move == TakeThreeMove(Color.BLACK, Color.RED, Color.BLUE): #
            output = "t3krb"
        elif move == TakeThreeMove(Color.GREEN, Color.RED, Color.BLUE): #
            output = "t3erb"
        elif move == TakeThreeMove(Color.WHITE, Color.BLACK, None):
            output = "t3wk"
        elif move == TakeThreeMove(Color.WHITE, Color.GREEN, None):
            output = "t3we"
        elif move == TakeThreeMove(Color.WHITE, Color.RED, None): #
            output = "t3wr"
        elif move == TakeThreeMove(Color.WHITE, Color.BLUE, None): #
            output = "t3wb"
        elif move == TakeThreeMove(Color.BLACK, Color.GREEN, None):
            output = "t3ke"
        elif move == TakeThreeMove(Color.BLACK, Color.RED, None):
            output = "t3kr"
        elif move == TakeThreeMove(Color.BLACK, Color.BLUE, None): #
            output = "t3kb"
        elif move == TakeThreeMove(Color.GREEN, Color.RED, None):
            output = "t3er"
        elif move == TakeThreeMove(Color.GREEN, Color.BLUE, None): #
            output = "t3eb"
        elif move == TakeThreeMove(Color.RED, Color.BLUE, None):
            output = "t3rb"
        elif move == TakeThreeMove(Color.WHITE, None, None):
            output = "t3w"
        elif move == TakeThreeMove(Color.BLACK, None, None):
            output = "t3k"
        elif move == TakeThreeMove(Color.GREEN, None, None):
            output = "t3e"
        elif move == TakeThreeMove(Color.RED, None, None):
            output = "t3r"
        elif move == TakeThreeMove(Color.BLUE, None, None):
            output = "t3b"
    elif isinstance(move, TakeTwoMove):
        if move == TakeTwoMove(Color.WHITE):
            output = "t2w"
        elif move == TakeTwoMove(Color.BLACK):
            output = "t2k"
        elif move == TakeTwoMove(Color.GREEN):
            output = "t2e"
        elif move == TakeTwoMove(Color.RED):
            output = "t2r"
        elif move == TakeTwoMove(Color.BLUE):
            output = "t2b"
    elif isinstance(move, Buy):
        if move == Buy(cpind, 0, True):
            output = "b1"
        elif move == Buy(cpind, 1, True):
            output = "b2"
        elif move == Buy(cpind, 2, True):
            output = "b3"
        elif move == Buy(1, 0, False):
            output = "b4"
        elif move == Buy(1, 1, False):
            output = "b5"
        elif move == Buy(1, 2, False):
            output = "b6"
        elif move == Buy(1, 3, False):
            output = "b7"
        elif move == Buy(2, 0, False):
            output = "b8"
        elif move == Buy(2, 1, False):
            output = "b9"
        elif move == Buy(2, 2, False):
            output = "b10"
        elif move == Buy(2, 3, False):
            output = "b11"
        elif move == Buy(3, 0, False):
            output = "b12"
        elif move == Buy(3, 1, False):
            output = "b13"
        elif move == Buy(3, 2, False):
            output = "b14"
        elif move == Buy(3, 3, False):
            output = "b15"
    elif isinstance(move, Discard):
        if move == Discard(Color.WHITE):
            output = "dw"
        elif move == Discard(Color.GREEN):
            output = "de"
        elif move == Discard(Color.BLACK):
            output = "dk"
        elif move == Discard(Color.RED):
            output = "dr"
        elif move == Discard(Color.BLUE):
            output = "db"
    else:
        output = ""

    return output
"""
Returns the AI the move should make. Uses determine_early_move if the AI has taken less than 10 turns (checking this might
require editing the main REPL and adding a field to the AI player). Otherwise, use determine_late_move.
"""
def determine_move(state):
    move = None
    if (state.get_current_player().get_num_moves() < 10):
        move = determine_early_move(state)
    else:
        move = determine_late_move(state)
    store_move(state, move)
    write_moves(state, csv=True)
    #if valid_move(state, move):
    standardized_move = standardize_move(move)
    if state.get_discarding():
        return convert_move(state, Discard(determine_discard(state)))
    # else:
    #     if isinstance(standardized_move, Buy):+ str(standardized_move.get_tier()) + " reserved : " + str(standardized_move.get_reserved()):
    #     return convert_move(state, standardized_move)
    #    return None #passing
        

################################# ATTEMPTERS ##################################



def attempt(state, move):
    cpSt = copy.deepcopy(state)
    return play(cpSt, move)


def attemptTakeTwo(state, color):
    move = TakeTwoMove(color)
    return attempt(state, move)


def attemptTakeThree(state, c1, c2, c3):
    move = TakeThreeMove(c1,c2,c3)
    return attempt(state, move)


def attemptBuy(state, tier, card, reserved):
    move = Buy(tier, card, reserved)
    return attempt(state, move)
    
    
def attemptNoble(state, noble):
    move = Buy_Noble(noble)
    return attempt(state, move)


def attemptTopReserve(state, tier):
    move = Reserve_Top(tier)
    return attempt(state, move)


def attemptReserve(state, tier, card):
    move = Reserve(tier, card)
    return attempt(state, move)


def attemptDiscard(state, color):
    move = Discard(color)
    return attempt(state, move)



############################### RANDOM MOVE ###################################



def allMoves():
    passMove = ["p"]
    take1gems = ["t3wke","t3wkr","t3wkb","t3wer","t3web","t3wrb","t3ker","t3keb","t3krb","t3erb","t3wk","t3we","t3wr","t3wb","t3ke","t3kr","t3kb","t3er","t3eb","t3rb","t3w","t3k","t3e","t3r","t3b"]
    take2gems = ["t2w","t2k","t2e","t2r","t2b"]
    buyAble = ["b1","b2","b3","b4","b5","b6","b7","b8","b9","b10","b11","b12","b13","b14","b15"]
    resAble = ["r1","r2","r3","r4","r5","r6","r7","r8","r9","r10","r11","r12","r13","r14","r15"]
    discardable = ["dg","dw","dk","de","dr","db"]
    return (passMove + take1gems + take2gems + buyAble + resAble + discardable)

def allMovesSplit():
    passMove = ["p"]
    take1gems = ["t3wke","t3wkr","t3wkb","t3wer","t3web","t3wrb","t3ker","t3keb","t3krb","t3erb","t3wk","t3we","t3wr","t3wb","t3ke","t3kr","t3kb","t3er","t3eb","t3rb","t3w","t3k","t3e","t3r","t3b"]
    take2gems = ["t2w","t2k","t2e","t2r","t2b"]
    buyAble = ["b1","b2","b3","b4","b5","b6","b7","b8","b9","b10","b11","b12","b13","b14","b15"]
    resAble = ["r1","r2","r3","r4","r5","r6","r7","r8","r9","r10","r11","r12","r13","r14","r15"]
    discardable = ["dg","dw","dk","de","dr","db"]
    return passMove, take1gems, take2gems, buyAble, resAble, discardable

def take1Possible(state, player):
    return state.possible_moves(player)[0:5]

def take2Possible(state, player):
    return state.possible_moves(player)[5:10]

def reservePossible(state, player):
    return state.possible_moves(player)[10:25]

def buyPossible(state, player):
    return state.possible_moves(player)[25:40]

def discardPossible(state, player):
    return state.possible_moves(player)[40:46]

def filterPossibleMoves(state):
    moves = []
    take1gems = np.array(["w","k","e","r","b"])
    take2gems = np.array(["t2w","t2k","t2e","t2r","t2b"])
    buyAble = np.array(["b1","b2","b3","b4","b5","b6","b7","b8","b9","b10","b11","b12","b13","b14","b15"])
    resAble = np.array(["r1","r2","r3","r4","r5","r6","r7","r8","r9","r10","r11","r12","r13","r14","r15"])
    discardable = np.array(["dg","dw","dk","de","dr","db"])
    
    p = state.get_current_player()
    masker = lambda m : np.array(list(map(lambda l:bool(l), m)))
    
    if (len(state.get_winners()) == 0):
        if (not state.get_discarding()):
            cpind = state.current_player_index()
            discardable = []
            t1p = np.array(take1Possible(state, cpind))
            t2p = np.array(take2Possible(state, cpind))
            rp = np.array(reservePossible(state, cpind))
            bp = np.array(buyPossible(state, cpind))
            if (sum(t1p) > 0):
                moves.append("TAKE3")
                mask = masker(t1p)
                take1gems = (take1gems[mask]).tolist()
            else:
                take1gems = []
            if (sum(t2p) > 0):
                moves.append("TAKE2")
                mask = masker(t2p)
                take2gems = (take2gems[mask]).tolist()
            else:
                take2gems = []
            if (sum(rp) > 0):
                moves.append("HOLD")
                mask = masker(rp)
                resAble = (resAble[mask]).tolist()
            else:
                resAble = []
            if (sum(bp) > 0):
                moves.append("BUY")
                mask = masker(bp)
                buyAble = (buyAble[mask]).tolist()
            else:
                buyAble = []
        else:
            take1gems = []
            take2gems = []
            buyAble = []
            resAble = []
            dp = np.array(discardPossible(state, state.current_player_index()))
            if (sum(discardPossible(state, state.current_player_index())) > 0):
                moves.append("DISCARD")
                mask = masker(dp)
                discardable = (discardable[mask]).tolist()
    else:
        moves = []
        take1gems = []
        take2gems = []
        buyAble = []
        resAble = []
        discardable = []
    
    return moves, take1gems, take2gems, buyAble, resAble, discardable

def make_t3(gemsSel):
    gems = copy.deepcopy(gemsSel)
    i = 0
    w = ""
    k = ""
    e = ""
    r = ""
    b = ""
    while (len(gems) > 0 and i != 3):
        ind = random.randint(0,len(gems)-1)
        gem = gems[ind]
        if gem == "w":
            w = gem
        elif gem == "k":
            k = gem
        elif gem == "e":
            e = gem
        elif gem == "r":
            r = gem
        elif gem == "b":
            b = gem
        del gems[ind]
        i += 1
    return ("t3" + w + k + e + r + b)

def randomMove(state):
    moves, take1gems, take2gems, buyAble, resAble, discardable = filterPossibleMoves(state)
    
    arg2 = []
    move = ""
    if (len(moves) != 0):
        move = moves[random.randint(0,len(moves)-1)]
        if (move == "TAKE2"):
            move = take2gems[random.randint(0,len(take2gems)-1)]
        elif (move == "TAKE3"):
            move = make_t3(take1gems)
        elif (move == "BUY"):
            move = buyAble[random.randint(0,len(buyAble)-1)]
        elif (move == "HOLD"):
            move = resAble[random.randint(0,len(resAble)-1)]
        elif (move == "DISCARD"):
            move = discardable[random.randint(0,len(discardable)-1)]
    elif len(state.get_winners()) != 0:
        move = "p"
    return move


def playerStep(state):
    cpSt = copy.deepcopy(state)
    for n in range(len(cpSt.get_nobles())):
        action = attemptNoble(cpSt,n)
        if (action != None):
            action.next_player()
            return action
    cpSt.next_player()
    return cpSt


def point_reward(old_state, new_state):
    if (new_state != None):
        pindex = old_state.current_player_index()
        p_old = old_state.get_players()[pindex]
        p_updated = new_state.get_players()[pindex]
        return (p_updated.get_points() - p_old.get_points())
    else:
        return 0


def reward_map(old_state, new_state):
    passMove = [0]
    take1gems = [0] * 25
    take2gems = [0] * 5
    bp = point_reward(old_state, new_state)
    buyAble = [bp,bp,bp,bp,bp,bp,bp,bp,bp,bp,bp,bp,bp,bp,bp]
    resAble = [0] * 15
    discardable = [0] * 6
    return (passMove + take1gems + take2gems + buyAble + resAble + discardable)


def outputState(oldState, output):
    try:
        state = copy.deepcopy(oldState)
        cpind = state.current_player_index()
        obsv_ = None
        reward = 0  # Invalid move
        if output == "p":
            obsv_ = playerStep(state)
        elif output == "t3wke":
            obsv_ = attemptTakeThree(state,Color.WHITE,Color.BLACK,Color.GREEN)
        elif output == "t3wkr":
            obsv_ = attemptTakeThree(state,Color.WHITE,Color.BLACK,Color.RED)
        elif output == "t3wkb":
            obsv_ = attemptTakeThree(state,Color.WHITE,Color.BLACK,Color.BLUE)
        elif output == "t3wer":
            obsv_ = attemptTakeThree(state,Color.WHITE,Color.GREEN,Color.RED)
        elif output == "t3web":
            obsv_ = attemptTakeThree(state,Color.WHITE,Color.GREEN,Color.BLUE)
        elif output == "t3wrb":
            obsv_ = attemptTakeThree(state,Color.WHITE,Color.RED,Color.BLUE)
        elif output == "t3ker":
            obsv_ = attemptTakeThree(state,Color.BLACK,Color.GREEN,Color.RED)
        elif output == "t3keb":
            obsv_ = attemptTakeThree(state,Color.BLACK,Color.GREEN,Color.BLUE)
        elif output == "t3krb":
            obsv_ = attemptTakeThree(state,Color.BLACK,Color.RED,Color.BLUE)
        elif output == "t3erb":
            obsv_ = attemptTakeThree(state,Color.GREEN,Color.RED,Color.BLUE)
        elif output == "t3wk":
            obsv_ = attemptTakeThree(state,Color.WHITE,Color.BLACK,None)
        elif output == "t3we":
            obsv_ = attemptTakeThree(state,Color.WHITE,Color.GREEN,None)
        elif output == "t3wr":
            obsv_ = attemptTakeThree(state,Color.WHITE,Color.RED,None)
        elif output == "t3wb":
            obsv_ = attemptTakeThree(state,Color.WHITE,Color.BLUE,None)
        elif output == "t3ke":
            obsv_ = attemptTakeThree(state,Color.BLACK,Color.GREEN,None)
        elif output == "t3kr":
            obsv_ = attemptTakeThree(state,Color.BLACK,Color.RED,None)
        elif output == "t3kb":
            obsv_ = attemptTakeThree(state,Color.BLACK,Color.BLUE,None)
        elif output == "t3er":
            obsv_ = attemptTakeThree(state,Color.GREEN,Color.RED,None)
        elif output == "t3eb":
            obsv_ = attemptTakeThree(state,Color.GREEN,Color.BLUE,None)
        elif output == "t3rb":
            obsv_ = attemptTakeThree(state,Color.RED,Color.BLUE,None)
        elif output == "t3w":
            obsv_ = attemptTakeThree(state,Color.WHITE,None,None)
        elif output == "t3k":
            obsv_ = attemptTakeThree(state,Color.BLACK,None,None)
        elif output == "t3e":
            obsv_ = attemptTakeThree(state,Color.GREEN,None,None)
        elif output == "t3r":
            obsv_ = attemptTakeThree(state,Color.RED,None,None)
        elif output == "t3b":
            obsv_ = attemptTakeThree(state,Color.BLUE,None,None)
        elif output == "t2w":
            obsv_ = attemptTakeTwo(state,Color.WHITE)
        elif output == "t2k":
            obsv_ = attemptTakeTwo(state,Color.BLACK)
        elif output == "t2e":
            obsv_ = attemptTakeTwo(state,Color.GREEN)
        elif output == "t2r":
            obsv_ = attemptTakeTwo(state,Color.RED)
        elif output == "t2b":
            obsv_ = attemptTakeTwo(state,Color.BLUE)
        elif output == "b1":
            obsv_ = attemptBuy(state,cpind, 0, True)
        elif output == "b2":
            obsv_ = attemptBuy(state,cpind, 1, True)
        elif output == "b3":
            obsv_ = attemptBuy(state,cpind, 2, True)
        elif output == "b4":
            obsv_ = attemptBuy(state,1, 0, False)
        elif output == "b5":
            obsv_ = attemptBuy(state,1, 1, False)
        elif output == "b6":
            obsv_ = attemptBuy(state,1, 2, False)
        elif output == "b7":
            obsv_ = attemptBuy(state,1, 3, False)
        elif output == "b8":
            obsv_ = attemptBuy(state,2, 0, False)
        elif output == "b9":
            obsv_ = attemptBuy(state,2, 1, False)
        elif output == "b10":
            obsv_ = attemptBuy(state,2, 2, False)
        elif output == "b11":
            obsv_ = attemptBuy(state,2, 3, False)
        elif output == "b12":
            obsv_ = attemptBuy(state,3, 0, False)
        elif output == "b13":
            obsv_ = attemptBuy(state,3, 1, False)
        elif output == "b14":
            obsv_ = attemptBuy(state,3, 2, False)
        elif output == "b15":
            obsv_ = attemptBuy(state,3, 3, False)
        elif output == "r1":
            obsv_ = attemptTopReserve(state,1)
        elif output == "r2":
            obsv_ = attemptReserve(state,1,0)
        elif output == "r3":
            obsv_ = attemptReserve(state,1,1)
        elif output == "r4":
            obsv_ = attemptReserve(state,1,2)
        elif output == "r5":
            obsv_ = attemptReserve(state,1,3)
        elif output == "r6":
            obsv_ = attemptTopReserve(state,2)
        elif output == "r7":
            obsv_ = attemptReserve(state,2,0)
        elif output == "r8":
            obsv_ = attemptReserve(state,2,1)
        elif output == "r9":
            obsv_ = attemptReserve(state,2,2)
        elif output == "r10":
            obsv_ = attemptReserve(state,2,3)
        elif output == "r11":
            obsv_ = attemptTopReserve(state,3)
        elif output == "r12":
            obsv_ = attemptReserve(state,3,0)
        elif output == "r13":
            obsv_ = attemptReserve(state,3,1)
        elif output == "r14":
            obsv_ = attemptReserve(state,3,2)
        elif output == "r15":
            obsv_ = attemptReserve(state,3,3)
        elif output == "dg":
            obsv_ = attemptDiscard(state,"G")
        elif output == "dw":
            obsv_ = attemptDiscard(state,"W")
        elif output == "dk":
            obsv_ = attemptDiscard(state,"K")
        elif output == "de":
            obsv_ = attemptDiscard(state,"E")
        elif output == "dr":
            obsv_ = attemptDiscard(state,"R")
        elif output == "db":
            obsv_ = attemptDiscard(state,"B")

        if obsv_ != None and output != "":
            reward = reward_map(state, obsv_)[allMoves().index(output)]
            if output != "p":
                obsv_ = processState(state, obsv_)

            if len(state.get_nobles()) > len(obsv_.get_nobles()):
                reward += 3
            
        return obsv_, reward
    except:
        return oldState, 0


def processState(old_state, new_state):
    cp = new_state.get_current_player()

    if (new_state.get_firstWinner() == None):
        if (cp.get_points() >= 15):
            new_state.set_firstWinner(cp.get_name())

    if cp.gemGoldAmt() <= 10:
        new_state = playerStep(new_state)
        new_state.set_discarding(False)
    else:
        new_state.set_discarding(True)
            
    return new_state



############################## GAME STATE #####################################



class GameState:
    def __init__(self):
        self._state = State(2,0)
        self._prevStates = []
        self._AI0 = AI(AI_Type.TRAINED, 3, "AI 0")
        self._AI1 = AI(AI_Type.TRAINED, 4, "AI 1")
        self._AI2 = AI(AI_Type.TRAINED, 5, "AI 2")
        self._AI3 = AI(AI_Type.TRAINED, 6, "AI 3")
        self._dqnLast = None
        
    def get_state(self):
        state = copy.deepcopy(self._state)
        return state
    
    def set_state(self, state):
        self._state = state
    
    def get_ai0(self):
        return self._AI0
    
    def get_ai1(self):
        return self._AI1
    
    def get_ai2(self):
        return self._AI2
    
    def get_ai3(self):
        return self._AI3
    
    def get_DQN_move(self):
        return self._dqnLast
    
    def set_DQN_move(self, move):
        self._dqnLast = move
    
    def reset_AI_gameData(self):
        self._AI0.reset_gameData()
        self._AI1.reset_gameData()
        self._AI2.reset_gameData()
        self._AI3.reset_gameData()
    
    def playingAI(self):
        cp = self._state.get_current_player()
        if (cp.get_name() == "AI 0"):
            return self._AI0
        elif (cp.get_name() == "AI 1"):
            return self._AI1
        elif (cp.get_name() == "AI 2"):
            return self._AI2
        elif (cp.get_name() == "AI 3"):
            return self._AI3
        return None
    
    def get_prevStates(self):
        return self._prevStates
    
    def incr_inter(self):
        return self._state.incr_interactions()
    
    def add_state(self, state):
        self._prevStates.append(self._state)
        self._state = state
    
    def reinit(self, numPlayers, numAI):
        self._state = State(numPlayers, numAI)
        self.reset_AI_gameData()
        self._prevStates = []
        return self._state
    
    def end_game(self):
        maxPts = 15
        for p in self._state.get_players():
            if (p.get_points() > maxPts):
                maxPts = p.get_points()
                
        self._state.reset_winners()
        for p in self._state.get_players():
            if (p.get_points() == maxPts):
                self._state.add_winner(p.get_name())
        
        self._state.endGame()
        
    
    def step(self, action):
        cp = self._state.get_current_player()
        cpind = self._state.current_player_index()
        vld = valid_move(self._state, action, cpind)
        if vld:
            move = allMoves()[allMoves().index(action)]
        else:
            move = "invalid"
        
        obsv_ = None
        reward = 0
        if (move == "" or move == "invalid" or move == "notRunning"):
            obsv_ = self._state
        else:
            if self._state.running():
                reward = 0
                obsv_, reward = outputState(self._state, move)
                self._state = obsv_
                
                # Check if game has ended
                cp = self._state.get_current_player()
                if (self._state.get_firstWinner() == cp.get_name() or
                    deadlocked(self._state)):
                    self.end_game()
                            
                return self._state, reward, move
            else:
                return self._state, 0, "notRunning"
        return obsv_, 0, move
            

    def run_AI(self):
        cp = self._state.get_current_player()
        reward = 0
        mv = ""
        if self._state.running():
            if (cp.get_player_type()==PlayerType.AI):
                move = None
            if (cp.get_name() == "AI 0"):
                ai = self._AI0
            elif (cp.get_name() == "AI 1"):
                ai = self._AI1
            elif (cp.get_name() == "AI 2"):
                ai = self._AI2
            elif (cp.get_name() == "AI 3"):
                ai = self._AI3
                
            move = ai.makeMove(self._state)
            
            obsv_, reward, mv = self.step(move)
            if (mv != "" and mv != "invalid" and mv != "notRunning"):
                ai.incr_actionNum()
            if obsv_ != None:
                self._state = obsv_
        return self._state, reward, mv


def deadlocked(state):
    pchk = []
    for i in range(len(state.get_players())):
        mask = valid_moves(state, i)
        pchk.append(sum(mask[1:]))
    if sum(pchk) == 0:
        return 1
    return 0

def valid_moves(state, player):
    mask = [0] * 67
    if sum(discardPossible(state, player)) > 0:
        mask = [0] * 61 + discardPossible(state, player)
    else:
        t3mask = [0] * 25
        take1lst = take1Possible(state, player)
        canT1 = []
        clrLst = ["w", "k", "e", "r", "b"]
        for i in range(len(take1lst)):
            if take1lst[i]:
                canT1.append(clrLst[i])
        t3mvs = allMoves()[1:26]  # gets only the t3 moves
        for i in range(len(t3mvs)):
            for j in range(len(canT1)):
                if canT1[j] in t3mvs[i]:
                    t3mask[i] += 1
        all3 = t3mask[:10]
        just2 = t3mask[10:20]
        only1 = t3mask[20:]
        for i in range(len(all3)):
            t3mask[i] = int(all3[i] == 3)
        for i in range(len(just2)):
            t3mask[i+10] = int(just2[i] == 2)
        for i in range(len(only1)):
            t3mask[i+20] = int(only1[i] == 1)

        t2mask = take2Possible(state, player)
        bmask = buyPossible(state, player)
        rmask = reservePossible(state, player)

        nonPass = t3mask + t2mask + bmask + rmask + [0] * 6
        passMv = [0]
        if (sum(nonPass) == 0 or
            state.get_players()[player].get_player_type() == PlayerType.HUMAN):
            passMv = [1]
        mask = (passMv + nonPass)
    return mask


def stateMonster(state):
    return


def valid_move(state, move, player):
    mask = valid_moves(state, player)
    return mask[allMoves().index(move)]
 
 
def get_DQNmove(state):
    return gstate.get_DQN_move()


class AI_Type(Enum):
    RANDOM = 0
    STRICT = 1
    TRAINED = 2

class AI:
    def __init__(self, aitype, version, name):
        self._aitype = aitype
        self._version = version
        self._actionNum = 0
        self._score = 0
        self._reward = 0
        self._name = name
        rand = random.SystemRandom()
        self._policy = determine_move
        if (aitype == AI_Type.RANDOM):
            self._policy = randomMove
        elif (aitype == AI_Type.STRICT):
            self._policy = determine_move
        elif (aitype == AI_Type.TRAINED):
            self._policy = get_DQNmove
    
    def set_policy(self, p):
        self._policy = p
    
    def get_aitype(self):
        return self._aitype
    
    def get_actionNum(self):
        return self._actionNum
    
    def incr_actionNum(self):
        self._actionNum += 1
    
    def get_name(self):
        return self._name
    
    def get_version(self):
        return self._version
    
    def get_policy(self):
        return self._policy
    
    def get_model(self):
        return self._model
    
    def get_score(self):
        return self._score
    
    def set_score(self, score):
        self._score = score
    
    def get_reward(self):
        return self._reward
    
    def add_reward(self, rew):
        self._reward += rew
    
    def reset_gameData(self):
        self._reward = 0
        self._score = 0
        self._actionNum = 0
    
    def makeMove(self, state):
        cp = state.get_current_player()
        cpind = state.current_player_index()
        cp.incr_num_moves()
        if self._aitype == AI_Type.RANDOM:
            return self._policy(state)
        elif self._aitype == AI_Type.STRICT:
            return self._policy(state)
        else:
            return allMoves()[self._policy(state)]
    
    def won(self, state):
        return self._name in state.get_winners()



gstate = GameState()
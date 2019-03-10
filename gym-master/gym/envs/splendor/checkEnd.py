from gym.envs.splendor.structure import *
from gym.envs.splendor.game_controller import *

import copy
import kivy
import asyncio
import random
from datetime import datetime
import numpy as np
random.seed(datetime.now())
r = random.SystemRandom()

try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, NoTransition
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.properties import BooleanProperty
from kivy.config import Config

Config.set('graphics', 'width', '1440')
Config.set('graphics', 'height', '900')



Builder.load_string('''
<FontLabel@Label>
    font_name: "/Users/epalma/Desktop/splendor-gym/gym-master/gym/envs/splendor/saxmono.ttf"
    halign: "center"
    
<FontButton@Button>
    font_name: "/Users/epalma/Desktop/splendor-gym/gym-master/gym/envs/splendor/saxmono.ttf"
    background_color: 0,.4,.6,1
    halign: "center"
    
<FontToggleButton@ToggleButton>
    font_name: "/Users/epalma/Desktop/splendor-gym/gym-master/gym/envs/splendor/saxmono.ttf"
    background_color: 0,.4,.6,1
    halign: "center"


<ResetScreen@Screen>:
    name: "reset_screen"
    
    on_enter:
        root.manager.current = 'game_screen'


<GameScreen@Screen>:
    
    on_enter:
        root.update_state_view("reset_screen")
    
    BoxLayout:
        orientation: "vertical"
        
        BoxLayout:
            orientation: "horizontal"
            size_hint: 1.0, 0.05
            
            FontLabel:
                size_hint: 0.3, 1.0
                text: "GOAL: 15"
            
            FontLabel:
                size_hint: 0.2, 1.0
                halign: "right"
                text: "TURN :"
            
            FontLabel:
                id: turnCount
                size_hint: 0.1, 1.0
                halign: "left"
            
            FontLabel:
                id: playerTurnLabel
            
            FontLabel:
                size_hint: 0.3, 1.0
                text: "UNDO TURN"
            
            FontLabel:
                size_hint: 0.3, 1.0
                text: "QUIT"
                disabled: True
                    
        BoxLayout:
            orientation: "horizontal"
            
            BoxLayout:
                orientation: "vertical"
                
                BoxLayout:
                    orientation: "horizontal"
                    padding: 10, 10
                    
                    BoxLayout:
                        orientation: "horizontal"
                        
                        FontLabel:
                            id: p0r0
                        
                        FontLabel:
                            id: p0r1
                        
                        FontLabel:
                            id: p0r2
                        
                    FontLabel:
                        id: p0info
                
                BoxLayout:
                    orientation: "horizontal"
                    padding: 10, 10
                
                    BoxLayout:
                        orientation: "horizontal"
                        
                        FontLabel:
                            id: p1r0
                        
                        FontLabel:
                            id: p1r1
                        
                        FontLabel:
                            id: p1r2
                        
                    FontLabel:
                        id: p1info
                
                BoxLayout:
                    orientation: "horizontal"
                    padding: 10, 10
                
                    BoxLayout:
                        orientation: "horizontal"
                        
                        FontLabel:
                            id: p2r0
                        
                        FontLabel:
                            id: p2r1
                        
                        FontLabel:
                            id: p2r2
                        
                    FontLabel:
                        id: p2info
                
                BoxLayout:
                    orientation: "horizontal"
                    padding: 10, 10
                
                    BoxLayout:
                        orientation: "horizontal"
                        
                        FontLabel:
                            id: p3r0
                        
                        FontLabel:
                            id: p3r1
                        
                        FontLabel:
                            id: p3r2
                        
                    FontLabel:
                        id: p3info
                
                BoxLayout:
                    size_hint: 1.0, 0.5
                    orientation: "horizontal"
                    
                    FontLabel:
                        id: discInfo
                    
                    FontLabel:
                        id: discG
                    
                    FontLabel:
                        id: discW
                    
                    FontLabel:
                        id: discK
                    
                    FontLabel:
                        id: discE
                    
                    FontLabel:
                        id: discR
                    
                    FontLabel:
                        id: discB
                        
            
            BoxLayout:
                size_hint: 0.2, 1.0
                orientation: "vertical"
                padding: 10, 10
                
                FontLabel:
                    id: gemG
                    
                FontLabel:
                    id: gemW
                
                FontLabel:
                    id: gemK
                
                FontLabel:
                    id: gemE
                
                FontLabel:
                    id: gemR
                
                FontLabel:
                    id: gemB
                
            BoxLayout:
                orientation: "vertical"
                
                BoxLayout:
                    orientation: "horizontal"
                    padding: 10, 10
                
                    FontLabel:
                        id: nob0
                        
                    FontLabel:
                        id: nob1
                    
                    FontLabel:
                        id: nob2
                        
                    FontLabel:
                        id: nob3
                    
                    FontLabel:
                        id: nob4
                
                BoxLayout:
                    orientation: "horizontal"
                    padding: 10, 10
                
                    FontLabel:
                        id: t3i
                        
                    FontLabel:
                        id: t3c0
                    
                    FontLabel:
                        id: t3c1
                        
                    FontLabel:
                        id: t3c2
                    
                    FontLabel:
                        id: t3c3
                
                BoxLayout:
                    orientation: "horizontal"
                    padding: 10, 10
                
                    FontLabel:
                        id: t2i
                        
                    FontLabel:
                        id: t2c0
                    
                    FontLabel:
                        id: t2c1
                        
                    FontLabel:
                        id: t2c2
                    
                    FontLabel:
                        id: t2c3
                
                BoxLayout:
                    orientation: "horizontal"
                    padding: 10, 10
                
                    FontLabel:
                        id: t1i
                        
                    FontLabel:
                        id: t1c0
                    
                    FontLabel:
                        id: t1c1
                        
                    FontLabel:
                        id: t1c2
                    
                    FontLabel:
                        id: t1c3
                    
        BoxLayout:
            orientation: "horizontal"
            size_hint: 1.0, 0.1
            
            FontButton:
                id: passButton
                text: "PASS"
                on_release:
                    root.update_state_view("reset_screen")
            
            FontLabel:
                id: discard
                text: "DISCARD"
            
            FontLabel:
                id: take2
                text: "TAKE 2\\nALIKE"
                    
            FontLabel:
                id: take3
                text: "TAKE UP TO 3\\nDISTINCT"
                    
            FontLabel:
                id: buy
                text: "BUY"
            
            FontLabel:
                id: hold
                text: "HOLD"
''')
        
 
class GameScreen(Screen):
    
    def __init__(self, **kw):

        # Initialize
        super(Screen, self).__init__(**kw)
    
    ############################## VARIABLES ##################################
    

    _state = pickle.load(open('./gstate.pkl', 'rb'))
    _gemsSelected = []
    _discardNewState = 0
    _take2NewState = 0
    _take3NewState = 0
    _buyNewState = 0
    _holdNewState = 0
    _notDQN_AI = True
    _prevGameCt = 0
    
    def getState(self):
        return self._state
    
    def setState(self, state):
        self._state = pickle.load(open('./gstate.pkl', 'rb'))
        self.render()
        
    def update_state_view(self, scr):
        try:
            gc = pickle.load(open('./done.pkl', 'rb'))
            if gc > self._prevGameCt:
                self._prevGameCt = gc
                self._state = pickle.load(open('./gstate.pkl', 'rb'))
        except:
            try:
                gc = pickle.load(open('./done.pkl', 'rb'))
                if gc > self._prevGameCt:
                    self._prevGameCt = gc
                    self._state = pickle.load(open('./gstate.pkl', 'rb'))
            except:
                try:
                    gc = pickle.load(open('./done.pkl', 'rb'))
                    if gc > self._prevGameCt:
                        self._prevGameCt = gc
                        self._state = pickle.load(open('./gstate.pkl', 'rb'))
                except:
                    gc = pickle.load(open('./done.pkl', 'rb'))
                    if gc > self._prevGameCt:
                        self._prevGameCt = gc
                        self._state = pickle.load(open('./gstate.pkl', 'rb'))

        try:
            self.render()
            self.manager.current = scr
        except:
            return
        
        self.render()
        self.manager.current = scr
    
    def update(self, button):
        if button == "back":
            obsv_ = gstate.step("back")
            self._state = obsv_
        elif button == "next":
            obsv_ = gstate.step("p")
            self._state = obsv_
        elif button == "discard":
            self._discardNewState = processState(
                self._state, self._discardNewState)
            self.setState(self._discardNewState)
        elif button == "take2":
            self._take2NewState = processState(
                self._state, self._take2NewState)
            self.setState(self._take2NewState)
        elif button == "take3":
            self._take3NewState = processState(
                self._state, self._take3NewState)
            self.setState(self._take3NewState)
        elif button == "buy":
            self._buyNewState = processState(
                self._state, self._buyNewState)
            self.setState(self._buyNewState)
        elif button == "hold":
            self._holdNewState = processState(
                self._state, self._holdNewState)
            self.setState(self._holdNewState)
        self.manager.current = 'reset_screen'
    
    
    
    ############################## MASS RESETTERS ###########################
    
    
    
    def showDiscardOptions(self):
        self.disableButtons()
        self.ids.discInfo.text = "CHOOSE\nGEMS\nTO\nDISCARD"
        self.ids.discG.text = "G"
        self.ids.discW.text = "W"
        self.ids.discK.text = "K"
        self.ids.discE.text = "E"
        self.ids.discR.text = "R"
        self.ids.discB.text = "B"
    
    
    def hideDiscardOptions(self):
        self.ids.discInfo.text = ""
        self.ids.discG.text = ""
        self.ids.discW.text = ""
        self.ids.discK.text = ""
        self.ids.discE.text = ""
        self.ids.discR.text = ""
        self.ids.discB.text = ""
    
    
    def disableButtons(self):
        self._gemsSelected = []
    
    
    def clearText(self):
        self.ids.playerTurnLabel.text = ""
        self.ids.p0r0.text = ""
        self.ids.p0r1.text = ""
        self.ids.p0r2.text = ""
        self.ids.p0info.text = ""
        self.ids.p1r0.text = ""
        self.ids.p1r1.text = ""
        self.ids.p1r2.text = ""
        self.ids.p1info.text = ""
        self.ids.p2r0.text = ""
        self.ids.p2r1.text = ""
        self.ids.p2r2.text = ""
        self.ids.p2info.text = ""
        self.ids.p3r0.text = ""
        self.ids.p3r1.text = ""
        self.ids.p3r2.text = ""
        self.ids.p3info.text = ""
        self.ids.gemG.text = ""
        self.ids.gemW.text = ""
        self.ids.gemK.text = ""
        self.ids.gemE.text = ""
        self.ids.gemR.text = ""
        self.ids.gemB.text = ""
        self.ids.nob0.text = ""
        self.ids.nob1.text = ""
        self.ids.nob2.text = ""
        self.ids.nob3.text = ""
        self.ids.nob4.text = ""
        self.ids.t3i.text = ""
        self.ids.t3c0.text = ""
        self.ids.t3c1.text = ""
        self.ids.t3c2.text = ""
        self.ids.t3c3.text = ""
        self.ids.t2i.text = ""
        self.ids.t2c0.text = ""
        self.ids.t2c1.text = ""
        self.ids.t2c2.text = ""
        self.ids.t2c3.text = ""
        self.ids.t1i.text = ""
        self.ids.t1c0.text = ""
        self.ids.t1c1.text = ""
        self.ids.t1c2.text = ""
        self.ids.t1c3.text = ""
    
    
    
    ########################## GUI INFORMATION SETTERS ########################
    
    
    
    # Set Player Turn FontLabel
    def setPlayerTurnLabel(self):
        name = self._state.get_current_player().get_name()
        text = "It's " + str(name) + "'s Turn!"
        self.ids.playerTurnLabel.text = text
    
    
    def setTurnCount(self):
        self.ids.turnCount.text = str(self._state.get_turn_count())
    
    
    # Set info for reserved card for a player
    def setPlayerReservedCardInfo(self, player, card):
        res = self.getPlayerReserved(player,card)
        text = str(res)
        if (player == 0):
            if (card == 0):
                self.ids.p0r0.text = text
            elif (card == 1):
                self.ids.p0r1.text = text
            elif (card == 2):
                self.ids.p0r2.text = text
        elif (player == 1):
            if (card == 0):
                self.ids.p1r0.text = text
            elif (card == 1):
                self.ids.p1r1.text = text
            elif (card == 2):
                self.ids.p1r2.text = text
        elif (player == 2):
            if (card == 0):
                self.ids.p2r0.text = text
            elif (card == 1):
                self.ids.p2r1.text = text
            elif (card == 2):
                self.ids.p2r2.text = text
        elif (player == 3):
            if (card == 0):
                self.ids.p3r0.text = text
            elif (card == 1):
                self.ids.p3r1.text = text
            elif (card == 2):
                self.ids.p3r2.text = text
    
    
    # Set player points, name, gems owned, cards owned, and total points
    def setPlayerInfo(self, player):
        text = str(self._state.get_players()[player])
        if (player == 0):
            self.ids.p0info.text = text
        elif (player == 1):
            self.ids.p1info.text = text
        elif (player == 2):
            self.ids.p2info.text = text
        elif (player == 3):
            self.ids.p3info.text = text
    
    
    # Set amount of gems left for each type
    def setGemPoolAmount(self, gem):
        gems = self._state.get_avail_gems()
        w = gems.data_gui()[0]
        k = gems.data_gui()[1]
        e = gems.data_gui()[2]
        r = gems.data_gui()[3]
        b = gems.data_gui()[4]
        if (gem == 0):
            self.ids.gemG.text = ("(G)OLD" +"\n\n\n"+ str(self._state.get_num_gold()))
        elif (gem == 1):
            self.ids.gemW.text = ("(W)HITE" +"\n\n\n"+ str(w))
        elif (gem == 2):
            self.ids.gemK.text = ("BLAC(K)" +"\n\n\n"+ str(k))
        elif (gem == 3):
            self.ids.gemE.text = ("GR(E)EN" +"\n\n\n"+ str(e))
        elif (gem == 4):
            self.ids.gemR.text = ("(R)ED" +"\n\n\n"+ str(r))
        if (gem == 5):
            self.ids.gemB.text = ("(B)LUE" +"\n\n\n"+ str(b))
    
    
    # Set noble card points and gem cost
    def setNobleCardInfo(self, noble):
        nob = str(self.getNoble(noble))
        text = ("3" + "\n\n\n" + "W|K|E|R|B\n" + nob)
        if (noble == 0):
            self.ids.nob0.text = text
        elif (noble == 1):
            self.ids.nob1.text = text
        elif (noble == 2):
            self.ids.nob2.text = text
        elif (noble == 3):
            self.ids.nob3.text = text
        elif (noble == 4):
            self.ids.nob4.text = text
    
    
    # Set tier deck level and amount left
    def setTierDeckInfo(self, tier):
        if (tier == 0):
            num = str(len(self._state.get_tier1_deck()))
            self.ids.t1i.text = "Tier 1" +"\n\n\n"+ "("+num+")"
        elif (tier == 1):
            num = str(len(self._state.get_tier2_deck()))
            self.ids.t2i.text = "Tier 2" +"\n\n\n"+ "("+num+")"
        elif (tier == 2):
            num = str(len(self._state.get_tier3_deck()))
            self.ids.t3i.text = "Tier 3" +"\n\n\n"+ "("+num+")"
    
    
    # Set info for card placed on board at tier
    def setTierCardInfo(self, tier, card):
        if (tier == 0):
            text = str(self._state.getTierCard(1,card))
            if (card == 0):
                self.ids.t1c0.text = text
            elif (card == 1):
                self.ids.t1c1.text = text
            elif (card == 2):
                self.ids.t1c2.text = text
            elif (card == 3):
                self.ids.t1c3.text = text
        elif (tier == 1):
            text = str(self._state.getTierCard(2,card))
            if (card == 0):
                self.ids.t2c0.text = text
            elif (card == 1):
                self.ids.t2c1.text = text
            elif (card == 2):
                self.ids.t2c2.text = text
            elif (card == 3):
                self.ids.t2c3.text = text
        elif (tier == 2):
            text = str(self._state.getTierCard(3,card))
            if (card == 0):
                self.ids.t3c0.text = text
            elif (card == 1):
                self.ids.t3c1.text = text
            elif (card == 2):
                self.ids.t3c2.text = text
            elif (card == 3):
                self.ids.t3c3.text = text
    
    
    
    ############################ HELPER FUNCTIONS #############################
    
    
    
    def getPlayerReserved(self, player, card):
        self._state.get_players()[player].get_reserved()[card].reserve(card)
        return self._state.get_players()[player].get_reserved()[card]
    
    
    def getNoble(self, noble):
        return self._state.get_nobles()[noble]
    
    
    def disableDiscard(self, gem):
        action = attemptDiscard(self._state, gem)
        if (action != None):
            self._discardNewState = action
            return False
        else:
            self._discardNewState = action
        return True
        
    
    
    ########## RENDERING ##########
    
    
    
    def reset(self):
        self.clearText()
        
        self.disableButtons()
        
        self._discardNewState = 0
        self._take2NewState = 0
        self._take3NewState = 0
        self._buyNewState = 0
        self._holdNewState = 0
        
    
    def render(self):
        self.reset()
        
        numPlayers = len(self._state.get_players())
        resNums = []
        for i in range(numPlayers):
            resNums.append(len(self._state.get_players()[i].get_reserved()))
        numNobs = len(self._state.get_nobles())
        tcardNums =    [len(self._state.get_tier1()),
                        len(self._state.get_tier2()),
                        len(self._state.get_tier3())]
        
        self.setPlayerTurnLabel()
        self.setTurnCount()
        for p in range(numPlayers):
            for c in range(resNums[p]):
                self.setPlayerReservedCardInfo(p,c)
        for p in range(numPlayers):
            self.setPlayerInfo(p)
        for g in range(6):
            self.setGemPoolAmount(g)
        for n in range(numNobs):
            self.setNobleCardInfo(n)
        for t in range(3):
            self.setTierDeckInfo(t)
        for t in range(3):
            for c in range(tcardNums[t]):
                self.setTierCardInfo(t,c)
        
        if (self._state.get_discarding()):
            self.showDiscardOptions()
        else:
            self.hideDiscardOptions()
        if (not self._state.running()):
            self.ids.playerTurnLabel.text = self._state.get_winners_text()
            self.disableButtons()



    ######################### GUI FUNCTIONALITY ###############################
    
    
    
    def disableTakeTwo(self):
        gemsSel = self._gemsSelected
        if len(gemsSel) == 1:
            action = attemptTakeTwo(self._state, gemsSel[0])
            if (action != None):
                self._take2NewState = action
                return False
        return True
        
    
    def disableTakeThree(self):
        gemsSel = self._gemsSelected
        ln = len(gemsSel)
        if ln > 0 and ln < 4:
            gem0 = gemsSel[0]
            gem1 = None
            gem2 = None
            if ln > 1:
                gem1 = gemsSel[1]
            if ln > 2:
                gem2 = gemsSel[2]
            
            action = attemptTakeThree(self._state, gem0, gem1, gem2)
            if (action != None):
                self._take3NewState = action
                return False    
        return True
    
    
    def disableBuy(self, ctype, card):
        if ctype != 1:
            action = None
            if ctype == 0:
                action = attemptBuy(self._state, card[0], card[1], True)
            elif ctype == 2:
                action = attemptBuy(self._state, card[0], card[1], False)
               
            if (action != None):
                self._buyNewState = action
                return False 
        return True
            
            
    def disableHold(self, ctype, arg):
        if ctype != 0:
            if ctype == 1:
                action = attemptTopReserve(self._state, arg)
            elif ctype == 2:
                action = attemptReserve(self._state, arg[0], arg[1])
                
            if (action != None):
                self._holdNewState = action
                return False
        return True
    
    
    # Add gem to list of selected gems if adding is True, else delete.
    # Then create a move with the selected gems if applicable
    def gemActionToggle(self, gem, bState):
        c = Color.mapToColor(gem)
        
        # Check whether they are selecting or deselecting gem
        adding = False
        if (bState == "down"):
            adding = True
        if (adding):
            self._gemsSelected.append(c)
        else:
            self._gemsSelected.remove(c)


class ResetScreen(Screen):
    def __init__(self, **kw):

        # Initialize
        super(Screen, self).__init__(**kw)

class SplendorKivyApp(App):
 
    def build(self):
        # The ScreenManager controls moving between screens
        screen_manager = ScreenManager(transition=NoTransition())
         
        # Add the screens to the manager and then supply a name
        # that is used to switch screens
        screen_manager.add_widget(GameScreen(name="game_screen"))
        screen_manager.add_widget(ResetScreen(name="reset_screen"))
        
        return screen_manager


class kivy_screen_manager(ScreenManager):
    pass




splendor_gui = SplendorKivyApp()
splendor_gui.run()
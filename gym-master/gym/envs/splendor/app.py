from structure import *
from game_controller import *

import copy
import kivy
import asyncio
import random
from datetime import datetime
import numpy as np
random.seed(datetime.now())
r = random.SystemRandom()

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
    font_name: "./saxmono.ttf"
    halign: "center"
    
<FontButton@Button>
    font_name: "./saxmono.ttf"
    background_color: 0,.4,.6,1
    halign: "center"
    
<FontToggleButton@ToggleButton>
    font_name: "./saxmono.ttf"
    background_color: 0,.4,.6,1
    halign: "center"
    

<IntroScreen@Screen>:
    BoxLayout:
        orientation: "vertical"
        spacing: 10
        padding: 10
        
        FontLabel:
            text: "SPLENDOR"
        
        FontLabel:
            size_hint: 1.0, 0.3
            text: "Total Number of Players"
        
        BoxLayout:
            orientation: "horizontal"
            size_hint: 1.0, 0.4
            FontToggleButton:
                text: "2"
                group: "numPlayers"
                state: "down"
                on_press:
                    root.deselectFor(2)
                    root.setNumPlayers(2)
                allow_no_selection: False
            FontToggleButton:
                text: "3"
                group: "numPlayers"
                on_press:
                    root.deselectFor(3)
                    root.setNumPlayers(3)
                allow_no_selection: False
            FontToggleButton:
                text: "4"
                group: "numPlayers"
                on_press:
                    root.deselectFor(4)
                    root.setNumPlayers(4)
                allow_no_selection: False
          
        FontLabel:
            size_hint: 1.0, 0.3
            text: ""
        
        FontLabel:
            size_hint: 1.0, 0.3
            text: "How many of these players are AI?"
             
        BoxLayout:
            orientation: "horizontal"
            size_hint: 1.0, 0.4
            FontToggleButton:
                text: "0"
                group: "numAI"
                state: "down"
                allow_no_selection: False
                on_press: root.setNumAI(0)
            FontToggleButton:
                text: "1"
                group: "numAI"
                allow_no_selection: False
                on_press: root.setNumAI(1)
            FontToggleButton:
                id: numAI2
                text: "2"
                group: "numAI"
                allow_no_selection: False
                on_press: root.setNumAI(2)
            FontToggleButton:
                id: numAI3
                text: "3"
                group: "numAI"
                disabled: True
                allow_no_selection: False
                on_press: root.setNumAI(3)
            FontToggleButton:
                id: numAI4
                text: "4"
                group: "numAI"
                disabled: True
                allow_no_selection: False
                on_press: root.setNumAI(4)
        
        FontLabel:
            size_hint: 1.0, 0.3
            text: ""
        
        FontButton:
            size_hint: 1.0, 0.75
            text: "START GAME"
            on_release:
                root.startGame()
                root.manager.current = 'game_screen'
 
<GameScreen@Screen>:
    
    on_enter:
        root.update_state_view()
        p0r0.state = 'normal'
        p0r1.state = 'normal'
        p0r2.state = 'normal'
        p1r0.state = 'normal'
        p1r1.state = 'normal'
        p1r2.state = 'normal'
        p2r0.state = 'normal'
        p2r1.state = 'normal'
        p2r2.state = 'normal'
        p3r0.state = 'normal'
        p3r1.state = 'normal'
        p3r2.state = 'normal'
        gemW.state = 'normal'
        gemK.state = 'normal'
        gemE.state = 'normal'
        gemR.state = 'normal'
        gemB.state = 'normal'
        nob0.state = 'normal'
        nob1.state = 'normal'
        nob2.state = 'normal'
        nob3.state = 'normal'
        nob4.state = 'normal'
        t3i.state = 'normal'
        t3c0.state = 'normal'
        t3c1.state = 'normal'
        t3c2.state = 'normal'
        t3c3.state = 'normal'
        t2i.state = 'normal'
        t2c0.state = 'normal'
        t2c1.state = 'normal'
        t2c2.state = 'normal'
        t2c3.state = 'normal'
        t1i.state = 'normal'
        t1c0.state = 'normal'
        t1c1.state = 'normal'
        t1c2.state = 'normal'
        t1c3.state = 'normal'
        discG.state = 'normal'
        discW.state = 'normal'
        discK.state = 'normal'
        discE.state = 'normal'
        discR.state = 'normal'
        discB.state = 'normal'
        discard.disabled = True
        take2.disabled = True
        take3.disabled = True
        buy.disabled = True
        hold.disabled = True
        root.runAI()
    
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
            
            FontButton:
                size_hint: 0.3, 1.0
                text: "UNDO TURN"
                on_release:
                    root.update("back")
                    root.manager.current = 'reset_screen'
            
            FontButton:
                size_hint: 0.3, 1.0
                text: "QUIT"
                on_release:
                    root.manager.current = 'intro_screen'
                    
        BoxLayout:
            orientation: "horizontal"
            
            BoxLayout:
                orientation: "vertical"
                
                BoxLayout:
                    orientation: "horizontal"
                    padding: 10, 10
                    
                    BoxLayout:
                        orientation: "horizontal"
                        
                        FontToggleButton:
                            id: p0r0
                            group: "selection"
                            on_press:
                                root.cardActionToggle(0,[0,0])
                        
                        FontToggleButton:
                            id: p0r1
                            group: "selection"
                            on_press:
                                root.cardActionToggle(0,[0,1])
                        
                        FontToggleButton:
                            id: p0r2
                            group: "selection"
                            on_press:
                                root.cardActionToggle(0,[0,2])
                        
                    FontButton:
                        id: p0info
                
                BoxLayout:
                    orientation: "horizontal"
                    padding: 10, 10
                
                    BoxLayout:
                        orientation: "horizontal"
                        
                        FontToggleButton:
                            id: p1r0
                            group: "selection"
                            on_press:
                                root.cardActionToggle(0,[1,0])
                        
                        FontToggleButton:
                            id: p1r1
                            group: "selection"
                            on_press:
                                root.cardActionToggle(0,[1,1])
                        
                        FontToggleButton:
                            id: p1r2
                            group: "selection"
                            on_press:
                                root.cardActionToggle(0,[1,2])
                        
                    FontButton:
                        id: p1info
                
                BoxLayout:
                    orientation: "horizontal"
                    padding: 10, 10
                
                    BoxLayout:
                        orientation: "horizontal"
                        
                        FontToggleButton:
                            id: p2r0
                            group: "selection"
                            on_press:
                                root.cardActionToggle(0,[2,0])
                        
                        FontToggleButton:
                            id: p2r1
                            group: "selection"
                            on_press:
                                root.cardActionToggle(0,[2,1])
                        
                        FontToggleButton:
                            id: p2r2
                            group: "selection"
                            on_press:
                                root.cardActionToggle(0,[2,2])
                        
                    FontButton:
                        id: p2info
                
                BoxLayout:
                    orientation: "horizontal"
                    padding: 10, 10
                
                    BoxLayout:
                        orientation: "horizontal"
                        
                        FontToggleButton:
                            id: p3r0
                            group: "selection"
                            on_press:
                                root.cardActionToggle(0,[3,0])
                        
                        FontToggleButton:
                            id: p3r1
                            group: "selection"
                            on_press:
                                root.cardActionToggle(0,[3,1])
                        
                        FontToggleButton:
                            id: p3r2
                            group: "selection"
                            on_press:
                                root.cardActionToggle(0,[3,2])
                        
                    FontButton:
                        id: p3info
                
                BoxLayout:
                    size_hint: 1.0, 0.5
                    orientation: "horizontal"
                    
                    FontLabel:
                        id: discInfo
                    
                    FontToggleButton:
                        id: discG
                        group: "discard"
                        on_release:
                            root.disableDiscard("G")
                    
                    FontToggleButton:
                        id: discW
                        group: "discard"
                        on_release:
                            root.disableDiscard("W")
                    
                    FontToggleButton:
                        id: discK
                        group: "discard"
                        on_release:
                            root.disableDiscard("K")
                    
                    FontToggleButton:
                        id: discE
                        group: "discard"
                        on_release:
                            root.disableDiscard("E")
                    
                    FontToggleButton:
                        id: discR
                        group: "discard"
                        on_release:
                            root.disableDiscard("R")
                    
                    FontToggleButton:
                        id: discB
                        group: "discard"
                        on_release:
                            root.disableDiscard("B")
                        
            
            BoxLayout:
                size_hint: 0.2, 1.0
                orientation: "vertical"
                padding: 10, 10
                
                FontLabel:
                    id: gemG
                    
                FontToggleButton:
                    id: gemW
                    group: "white"
                    on_press: root.gemActionToggle("W",self.state)
                
                FontToggleButton:
                    id: gemK
                    group: "black"
                    on_press: root.gemActionToggle("K",self.state)
                
                FontToggleButton:
                    id: gemE
                    group: "green"
                    on_press: root.gemActionToggle("E",self.state)
                
                FontToggleButton:
                    id: gemR
                    group: "red"
                    on_press: root.gemActionToggle("R",self.state)
                
                FontToggleButton:
                    id: gemB
                    group: "blue"
                    on_press: root.gemActionToggle("B",self.state)
                
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
                
                    FontToggleButton:
                        id: t3i
                        group: "selection"
                        on_press:
                            root.cardActionToggle(1,3)
                        
                    FontToggleButton:
                        id: t3c0
                        group: "selection"
                        on_press:
                            root.cardActionToggle(2,[3,0])
                    
                    FontToggleButton:
                        id: t3c1
                        group: "selection"
                        on_press:
                            root.cardActionToggle(2,[3,1])
                        
                    FontToggleButton:
                        id: t3c2
                        group: "selection"
                        on_press:
                            root.cardActionToggle(2,[3,2])
                    
                    FontToggleButton:
                        id: t3c3
                        group: "selection"
                        on_press:
                            root.cardActionToggle(2,[3,3])
                
                BoxLayout:
                    orientation: "horizontal"
                    padding: 10, 10
                
                    FontToggleButton:
                        id: t2i
                        group: "selection"
                        on_press:
                            root.cardActionToggle(1,2)
                        
                    FontToggleButton:
                        id: t2c0
                        group: "selection"
                        on_press:
                            root.cardActionToggle(2,[2,0])
                    
                    FontToggleButton:
                        id: t2c1
                        group: "selection"
                        on_press:
                            root.cardActionToggle(2,[2,1])
                        
                    FontToggleButton:
                        id: t2c2
                        group: "selection"
                        on_press:
                            root.cardActionToggle(2,[2,2])
                    
                    FontToggleButton:
                        id: t2c3
                        group: "selection"
                        on_press:
                            root.cardActionToggle(2,[2,3])
                
                BoxLayout:
                    orientation: "horizontal"
                    padding: 10, 10
                
                    FontToggleButton:
                        id: t1i
                        group: "selection"
                        on_press:
                            root.cardActionToggle(1,1)
                        
                    FontToggleButton:
                        id: t1c0
                        group: "selection"
                        on_press:
                            root.cardActionToggle(2,[1,0])
                    
                    FontToggleButton:
                        id: t1c1
                        group: "selection"
                        on_press:
                            root.cardActionToggle(2,[1,1])
                        
                    FontToggleButton:
                        id: t1c2
                        group: "selection"
                        on_press:
                            root.cardActionToggle(2,[1,2])
                    
                    FontToggleButton:
                        id: t1c3
                        group: "selection"
                        on_press:
                            root.cardActionToggle(2,[1,3])
                    
        BoxLayout:
            orientation: "horizontal"
            size_hint: 1.0, 0.1
            
            FontButton:
                id: passButton
                text: "PASS TURN"
                on_release:
                    root.update("next")
                    root.manager.current = 'reset_screen'
            
            FontButton:
                id: discard
                text: "DISCARD"
                on_release:
                    root.update("discard")
                    root.manager.current = 'reset_screen'
            
            FontButton:
                id: take2
                text: "TAKE 2\\nALIKE"
                on_release:
                    root.update("take2")
                    root.manager.current = 'reset_screen'
                    
            FontButton:
                id: take3
                text: "TAKE UP TO 3\\nDISTINCT"
                on_release:
                    root.update("take3")
                    root.manager.current = 'reset_screen'
                    
            FontButton:
                id: buy
                text: "BUY"
                on_release:
                    root.update("buy")
                    root.manager.current = 'reset_screen'
            
            FontButton:
                id: hold
                text: "HOLD"
                on_release:
                    root.update("hold")
                    root.manager.current = 'reset_screen'

<ResetScreen@Screen>:
    on_enter:
        root.manager.current = 'game_screen'
''')


class SplendorKivyApp(App):
 
    def build(self):
        # The ScreenManager controls moving between screens
        screen_manager = ScreenManager(transition=NoTransition())
         
        # Add the screens to the manager and then supply a name
        # that is used to switch screens
        screen_manager.add_widget(IntroScreen(name="intro_screen"))
        screen_manager.add_widget(GameScreen(name="game_screen"))
        screen_manager.add_widget(ResetScreen(name="reset_screen"))
        
        return screen_manager


class kivy_screen_manager(ScreenManager):
        pass

class IntroScreen(Screen):
    
    _numPlayers = 2
    _numAI = 0
    
    def deselectFor(self, num):
        if (num == 2):
            self.ids.numAI3.disabled = True
            self.ids.numAI4.disabled = True
            if (self.ids.numAI3.state == "down" or
                self.ids.numAI4.state == "down"):
                self.ids.numAI2.state = "down"
                self._numAI = 2
            self.ids.numAI3.state = "normal"
            self.ids.numAI4.state = "normal"
        if (num == 3):
            self.ids.numAI3.disabled = False
            self.ids.numAI4.disabled = True
            if (self.ids.numAI4.state == "down"):
                self.ids.numAI3.state = "down"
                self._numAI = 3
            self.ids.numAI4.state = "normal"
        if (num == 4):
            self.ids.numAI3.disabled = False
            self.ids.numAI4.disabled = False
            
    def setNumPlayers(self, num):
        self._numPlayers = num
        
    def setNumAI(self, num):
        self._numAI = num
        
    def startGame(self):
        gscreen = self.manager.get_screen("game_screen")
        gstate.reinit(self._numPlayers-self._numAI, self._numAI)
        gscreen.setState(gstate.get_state())
        self.manager.current = 'reset_screen'
        
 
class GameScreen(Screen):
    
    
    
    ############################## VARIABLES ##################################
    
    
    
    _state = None
    _gemsSelected = []
    _discardNewState = 0
    _take2NewState = 0
    _take3NewState = 0
    _buyNewState = 0
    _holdNewState = 0
    
    def getState(self):
        return self._state
    
    def setState(self, state):
        self._state = state
        gstate.add_state(state)
        self.render()
        self.manager.current = 'reset_screen'
    
    
    def runAI(self):
        if (self._state.running()):
            cp = self._state.get_current_player()
            if (cp.get_player_type() == PlayerType.AI):
                gstate.run_AI()
                self.setState(gstate.get_state())
    
    def update_state_view(self):
        self._state = gstate.get_state()
        self.render()
    
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
        self.ids.discG.disabled = (not bool(self._state.possible_moves(self._state.current_player_index())[-6]))
        self.ids.discW.disabled = (not bool(self._state.possible_moves(self._state.current_player_index())[-5]))
        self.ids.discK.disabled = (not bool(self._state.possible_moves(self._state.current_player_index())[-4]))
        self.ids.discE.disabled = (not bool(self._state.possible_moves(self._state.current_player_index())[-3]))
        self.ids.discR.disabled = (not bool(self._state.possible_moves(self._state.current_player_index())[-2]))
        self.ids.discB.disabled = (not bool(self._state.possible_moves(self._state.current_player_index())[-1]))
        self.ids.passButton.disabled = True
    
    
    def hideDiscardOptions(self):
        self.ids.discInfo.text = ""
        self.ids.discG.text = ""
        self.ids.discW.text = ""
        self.ids.discK.text = ""
        self.ids.discE.text = ""
        self.ids.discR.text = ""
        self.ids.discB.text = ""
        self.ids.discG.disabled = True
        self.ids.discW.disabled = True
        self.ids.discK.disabled = True
        self.ids.discE.disabled = True
        self.ids.discR.disabled = True
        self.ids.discB.disabled = True
        self.ids.discard.disabled = True
        self.ids.passButton.disabled = False
    
    
    def disableButtons(self):
        self.ids.p0r0.disabled = True
        self.ids.p0r1.disabled = True
        self.ids.p0r2.disabled = True
        self.ids.p0info.disabled = True
        self.ids.p1r0.disabled = True
        self.ids.p1r1.disabled = True
        self.ids.p1r2.disabled = True
        self.ids.p1info.disabled = True
        self.ids.p2r0.disabled = True
        self.ids.p2r1.disabled = True
        self.ids.p2r2.disabled = True
        self.ids.p2info.disabled = True
        self.ids.p3r0.disabled = True
        self.ids.p3r1.disabled = True
        self.ids.p3r2.disabled = True
        self.ids.p3info.disabled = True
        self.ids.gemW.disabled = True
        self.ids.gemK.disabled = True
        self.ids.gemE.disabled = True
        self.ids.gemR.disabled = True
        self.ids.gemB.disabled = True
        self.ids.t3i.disabled = True
        self.ids.t3c0.disabled = True
        self.ids.t3c1.disabled = True
        self.ids.t3c2.disabled = True
        self.ids.t3c3.disabled = True
        self.ids.t2i.disabled = True
        self.ids.t2c0.disabled = True
        self.ids.t2c1.disabled = True
        self.ids.t2c2.disabled = True
        self.ids.t2c3.disabled = True
        self.ids.t1i.disabled = True
        self.ids.t1c0.disabled = True
        self.ids.t1c1.disabled = True
        self.ids.t1c2.disabled = True
        self.ids.t1c3.disabled = True
        self.ids.discG.disabled = True
        self.ids.discW.disabled = True
        self.ids.discK.disabled = True
        self.ids.discE.disabled = True
        self.ids.discR.disabled = True
        self.ids.discB.disabled = True
        self.ids.discard.disabled = True
        self._gemsSelected = []
        self.ids.take2.disabled = True
        self.ids.take3.disabled = True
        self.ids.buy.disabled = True
        self.ids.hold.disabled = True
    
    
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
                if (player == self._state.current_player_index()):
                    self.ids.p0r0.disabled = False
            elif (card == 1):
                self.ids.p0r1.text = text
                if (player == self._state.current_player_index()):
                    self.ids.p0r1.disabled = False
            elif (card == 2):
                self.ids.p0r2.text = text
                if (player == self._state.current_player_index()):
                    self.ids.p0r2.disabled = False
        elif (player == 1):
            if (card == 0):
                self.ids.p1r0.text = text
                if (player == self._state.current_player_index()):
                    self.ids.p1r0.disabled = False
            elif (card == 1):
                self.ids.p1r1.text = text
                if (player == self._state.current_player_index()):
                    self.ids.p1r1.disabled = False
            elif (card == 2):
                self.ids.p1r2.text = text
                if (player == self._state.current_player_index()):
                    self.ids.p1r2.disabled = False
        elif (player == 2):
            if (card == 0):
                self.ids.p2r0.text = text
                if (player == self._state.current_player_index()):
                    self.ids.p2r0.disabled = False
            elif (card == 1):
                self.ids.p2r1.text = text
                if (player == self._state.current_player_index()):
                    self.ids.p2r1.disabled = False
            elif (card == 2):
                self.ids.p2r2.text = text
                if (player == self._state.current_player_index()):
                    self.ids.p2r2.disabled = False
        elif (player == 3):
            if (card == 0):
                self.ids.p3r0.text = text
                if (player == self._state.current_player_index()):
                    self.ids.p3r0.disabled = False
            elif (card == 1):
                self.ids.p3r1.text = text
                if (player == self._state.current_player_index()):
                    self.ids.p3r1.disabled = False
            elif (card == 2):
                self.ids.p3r2.text = text
                if (player == self._state.current_player_index()):
                    self.ids.p3r2.disabled = False
    
    
    # Set player points, name, gems owned, cards owned, and total points
    def setPlayerInfo(self, player):
        text = str(self._state.get_players()[player])
        if (player == 0):
            self.ids.p0info.text = text
            self.ids.p0info.disabled = False
        elif (player == 1):
            self.ids.p1info.text = text
            self.ids.p1info.disabled = False
        elif (player == 2):
            self.ids.p2info.text = text
            self.ids.p2info.disabled = False
        elif (player == 3):
            self.ids.p3info.text = text
            self.ids.p3info.disabled = False
    
    
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
            if (int(w) != 0):
                self.ids.gemW.disabled = False
        elif (gem == 2):
            self.ids.gemK.text = ("BLAC(K)" +"\n\n\n"+ str(k))
            if (int(k) != 0):
                self.ids.gemK.disabled = False
        elif (gem == 3):
            self.ids.gemE.text = ("GR(E)EN" +"\n\n\n"+ str(e))
            if (int(e) != 0):
                self.ids.gemE.disabled = False
        elif (gem == 4):
            self.ids.gemR.text = ("(R)ED" +"\n\n\n"+ str(r))
            if (int(r) != 0):
                self.ids.gemR.disabled = False
        if (gem == 5):
            self.ids.gemB.text = ("(B)LUE" +"\n\n\n"+ str(b))
            if (int(b) != 0):
                self.ids.gemB.disabled = False
    
    
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
            if (num != 0):
                self.ids.t1i.disabled = False
        elif (tier == 1):
            num = str(len(self._state.get_tier2_deck()))
            self.ids.t2i.text = "Tier 2" +"\n\n\n"+ "("+num+")"
            if (num != 0):
                self.ids.t2i.disabled = False
        elif (tier == 2):
            num = str(len(self._state.get_tier3_deck()))
            self.ids.t3i.text = "Tier 3" +"\n\n\n"+ "("+num+")"
            if (num != 0):
                self.ids.t3i.disabled = False
    
    
    # Set info for card placed on board at tier
    def setTierCardInfo(self, tier, card):
        if (tier == 0):
            text = str(self._state.getTierCard(1,card))
            if (card == 0):
                self.ids.t1c0.text = text
                self.ids.t1c0.disabled = False
            elif (card == 1):
                self.ids.t1c1.text = text
                self.ids.t1c1.disabled = False
            elif (card == 2):
                self.ids.t1c2.text = text
                self.ids.t1c2.disabled = False
            elif (card == 3):
                self.ids.t1c3.text = text
                self.ids.t1c3.disabled = False
        elif (tier == 1):
            text = str(self._state.getTierCard(2,card))
            if (card == 0):
                self.ids.t2c0.text = text
                self.ids.t2c0.disabled = False
            elif (card == 1):
                self.ids.t2c1.text = text
                self.ids.t2c1.disabled = False
            elif (card == 2):
                self.ids.t2c2.text = text
                self.ids.t2c2.disabled = False
            elif (card == 3):
                self.ids.t2c3.text = text
                self.ids.t2c3.disabled = False
        elif (tier == 2):
            text = str(self._state.getTierCard(3,card))
            if (card == 0):
                self.ids.t3c0.text = text
                self.ids.t3c0.disabled = False
            elif (card == 1):
                self.ids.t3c1.text = text
                self.ids.t3c1.disabled = False
            elif (card == 2):
                self.ids.t3c2.text = text
                self.ids.t3c2.disabled = False
            elif (card == 3):
                self.ids.t3c3.text = text
                self.ids.t3c3.disabled = False
    
    
    
    ############################ HELPER FUNCTIONS #############################
    
    
    
    def getPlayerReserved(self, player, card):
        self._state.get_players()[player].get_reserved()[card].reserve(card)
        return self._state.get_players()[player].get_reserved()[card]
    
    
    def getNoble(self, noble):
        return self._state.get_nobles()[noble]
    
    
    def disableDiscard(self, gem):
        action = attemptDiscard(gem)
        if (action != None):
            self._discardNewState = action
            self.ids.discard.disabled = False
            return False
        else:
            self._discardNewState = action
            self.ids.discard.disabled = True
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
            self.ids.passButton.disabled = True



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
        
        self.ids.take2.disabled = self.disableTakeTwo()
        self.ids.take3.disabled = self.disableTakeThree()
    
    
    def cardActionToggle(self, ctype, item):
        self.ids.buy.disabled = self.disableBuy(ctype, item)
        self.ids.hold.disabled = self.disableHold(ctype, item)
    
    

@asyncio.coroutine
def delayed_result(delay, result):
        yield from asyncio.sleep(delay)
        return result

class ResetScreen(Screen):
    pass



splendor_gui = SplendorKivyApp()
splendor_gui.run()
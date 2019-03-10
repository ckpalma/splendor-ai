from gym.envs.splendor.game_controller import *
import numpy as np
import random
import subprocess
from datetime import datetime

try:
    import cPickle as pickle
except ModuleNotFoundError:
    import pickle

import gym
from gym import error, spaces, utils
from gym.utils import seeding

class SplendorEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        self.path = "../gym-master/gym/envs/splendor/"
        self.bpath = "../baselines-master/baselines/common/"
        self.observation_space = spaces.MultiDiscrete([1]*397)
        self.action_space = spaces.Discrete(67)
        self.reward_range = (0,8)
        self.stepNum = 0
        self.prevValid = ""
        self.prevRew = 0
        self.sumPoss = 0
        self.dl = 0
        self.numGames = pickle.load(open(self.path+'done.pkl', 'rb'))
        self.rewardAcc = 0
        self.prevTurnCtEnd = "N/A"
        self.version = pickle.load(open(self.bpath+'latest.pkl', 'rb'))
        pickle.dump(self.version+1, open(self.bpath+'latest.pkl', 'wb'),-1)
        # self.version = 0
        # pickle.dump(self.version, open(self.bpath+'latest.pkl', 'wb'),-1)
        self.minStepEnd = pickle.load(open(self.path+'minStep.pkl', 'rb'))
        # self.minStepEnd = 10000
        # pickle.dump(self.minStepEnd, open(self.path+'minStep.pkl', 'wb'),-1)
        self.logHist = pickle.load(open(self.path+'log.pkl', 'rb'))
        self.gameLog = []
        print("Training Splendor PPO2 Version: " + str(self.version+1))
        
    
    def step(self, action):
        
        self.stepNum += 1
        
        gstate.set_DQN_move(action)
        
        obsv_, reward, move = gstate.run_AI()
        self.rewardAcc += reward
        
        tc = obsv_.get_turn_count()
        cpind = obsv_.current_player_index()
        if move != "invalid":
            self.prevValid = move
            self.prevRew = reward
            mask = valid_moves(obsv_, cpind)
            self.sumPoss = sum(mask[1:])
            self.dl = deadlocked(obsv_)
        
        gstate.incr_inter()
        
        if (obsv_.running()):
            if (self.minStepEnd < self.stepNum):
                gstate.end_game()
        if (not obsv_.running()):
            pickle.dump(gstate.get_state(),
                open(self.path+'gstate.pkl','wb'), -1)
            self.prevTurnCtEnd = obsv_.get_turn_count()
            if self.stepNum <= self.minStepEnd and not self.dl:
                self.minStepEnd = self.stepNum - 1
                pickle.dump(self.minStepEnd, open(self.path+'minStep.pkl', 'wb'), -1)
            self.gameLog = [self.numGames,self.stepNum,self.rewardAcc]
            self.logHist.append(self.gameLog)
            self.numGames += 1
            pickle.dump(self.numGames, open(self.path+'done.pkl','wb'), -1)
            pickle.dump(self.logHist, open(self.path+'log.pkl','wb'), -1)
        
        sp_str = str(self.sumPoss)
        
        if tc > 2:
            print(" STEP: " + str(self.stepNum) + " | POSS: " + " "*(2-len(sp_str)) + sp_str + " | DL: " + str(self.dl) + " | GAME: " + str(self.numGames) + " | TURNS: " + str(tc) + " | REW: " + str(self.rewardAcc) + " | PREV_MOVE: (" + self.prevValid + ", " + str(self.prevRew) + ")" +
                "                             ", end="\r")        
        
        return obsv_.input_info(self.minStepEnd-self.stepNum), reward, (not obsv_.running()), {}
    
    def endResult(self):
        self.moveCursorUp(4)
        print("                       ")
        print("                       ")
        tct = str(gstate.get_state().get_turn_count())
        print("TURN COUNT: " + tct + " "*(11-len(tct)))
        print("                       ")
        sn = str(self.stepNum)
        sp = str(self.sumPoss)
        pv = self.prevValid
        pr = str(self.prevRew)
        print("STEP NUMBER: " + sn + " "*(10-len(sn)))
        print("sumPoss: " + sp + " "*(14-len(sp)))
        print("move: " + pv + " "*(17-len(pv)))
        print("reward: " + pr + " "*(15-len(pr)))
        print("                       ")
        for p in gstate.get_state().get_players():
            print("                       ")
            print(p)
        print("                       ")
        print("                       ")
        print("                       ")
        print("                       ")
        if gstate.get_state().running():
            self.moveCursorUp(45)
        else:
            txt = gstate.get_state().get_winners_text()
            print("--" + "-"*len(txt) + "--")
            print("| " + gstate.get_state().get_winners_text() + " |")
            print("--" + "-"*len(txt) + "--" + "\n\n\n\n")
    
    def moveCursorUp(self,nx):
        for i in range(nx):
            sys.stdout.write("\033[F")
    
    def reset(self):
        gstate.reinit(0,4)
        self.stepNum = 0
        self.rewardAcc = 0
        self.prevRew = 0
        self.gameLog = []
        print()
        return gstate.get_state().input_info(self.minStepEnd-self.stepNum)
    
    def render(self, mode='human', close=False):
        pickle.dump(gstate.get_state(), open(self.path+'gstate.pkl', 'wb'),-1)
    
    def seed(self, seed=None):
        if seed == None:
            seed = self.numGames
        setSeed(seed)
        return [seed]
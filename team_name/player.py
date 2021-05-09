from referee.game import *
from team_name.state import *
import random
import numpy as py
#python -m referee team_name team_name
#python -m referee team_name rand/player
#python -m battleground team_name NMSL greedy
#python -m battleground team_name NMSL bhy

class Player:
    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        # put your code here
        #initial state
        self.state = State()
        #assign a colour to the player
        self.player = player
        if(player == "lower"):
            self.opponent_color = "upper"
        else:
            self.opponent_color = "lower" 

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        # put your code here
        player_actions = list(self.state.available_actions(self.player, 1))
        opponent_actions = list(self.state.available_actions(self.player, -1))
        if(self.state.throws["upper"] == 0):
            return random.choice(player_actions)
        #
        #

        minimum = -np.inf
        chosen_action = None      
        # the minimax goes here
        for player_action in player_actions:                        
            maximun = np.inf
            for opponent_action in opponent_actions:
                action, defeated = self.state.update_state(opponent_action, player_action, self.player)
                current_utility = self.state.evaluation(self.player)
                
                self.state.Backtracking(action,defeated)                
                # a-b purning
                                
                if current_utility < maximun:
                    if current_utility <= minimum:
                        maximum = -np.inf #  no longer consider this action
                        break
                    maximum = current_utility
        # 
            if maximum > minimum:
                chosen_action = player_action
                minimum = maximum        
        #player_action= random.choice(player_actions)
        return chosen_action
        
        
    
    def update(self, opponent_action, player_action):
        
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        # put your code here
        self.state.update_state(opponent_action, player_action, self.player)

    


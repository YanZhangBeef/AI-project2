from referee.game import *
from NeverMindSomeLosers.state import *
import random
import numpy as py
#python -m referee team_name team_name

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
        print("rand  ======" + "  " + player)
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
        return random.choice(player_actions)
        
        
    
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

    


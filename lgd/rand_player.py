from lgd.game import *
from itertools import product
import numpy as np
from lgd.eval import evaluation
import random

import time

class Player:
    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        self.sim_game = Game()
        self.image = dict()
        self.name = player
        if player == "upper":
            self.opp = "lower"
        else:
            self.opp = "upper"

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """

        upper_actions = list(self.sim_game.available_actions("upper"))
        lower_actions = list(self.sim_game.available_actions("lower"))

        if self.name == "upper":
            return random.choice(upper_actions)
        else:
            return random.choice(lower_actions)

    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        if self.name == "upper":
            self.sim_game.update(player_action, opponent_action)
        else:
            self.sim_game.update(opponent_action, player_action)

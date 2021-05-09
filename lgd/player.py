from lgd.game import *
from itertools import product
import numpy as np
from lgd.eval import evaluation
import random

import time


def merge(update, active):
    for key, val in update.items():
        active[key] = val

    return active


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
        self.name = player
        if player == "upper":
            self.opp = "lower"
        else:
            self.opp = "upper"

        # piece count on board [R S P r s p]
        self.weight = [1, 1, 1, 1]

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """

        upper_actions = list(self.sim_game.available_actions("upper"))
        lower_actions = list(self.sim_game.available_actions("lower"))

        timer = time.process_time()

        ct = 0
        siz = 0
        # avoid some obviously no good steps for player side
        if self.name == "upper":
            for upp in upper_actions:
                try:
                    if self.sim_game.avoid(upp, self.name):
                        upper_actions.remove(upp)
                        ct += 1
                except KeyError:
                    continue
        else:
            for loo in lower_actions:
                try:
                    if self.sim_game.avoid(loo, self.name):
                        lower_actions.remove(loo)
                        ct += 1
                except KeyError:
                    continue

        best_score, lyr_best = -1, -1
        best_move = None
        for (upp, loo) in product(upper_actions, lower_actions):
            # break decision making if time limit passed
            if time.process_time() - timer > 5:
                break

            snapshot, throw, battles, move = self.sim_game.update(upp, loo)
            u_s, l_s = evaluation(self.sim_game.board, self.sim_game.throws["upper"],
                                  self.sim_game.throws["lower"], self.weight)

            # upper handler
            if self.name == "upper":
                # pruning: if the current move score is worse than the best already found, skip
                if u_s >= lyr_best:
                    lyr_best = u_s
                    best_move = upp
                else:
                    self.sim_game.revert(move, battles, throw)
                    continue

                # pruning: only expand moves where upper is "winning" over lower
                if u_s >= l_s:
                    pack = product(
                            list(self.sim_game.available_actions("upper")),
                            list(self.sim_game.available_actions("lower"))
                    )
                    siz += len(list(pack))
                    for (_upp, _loo) in pack:
                        ct += 1
                        _snapshot, _throw, _battles, _move = self.sim_game.update(_upp, _loo)

                        _u_s, _l_s = evaluation(self.sim_game.board, self.sim_game.throws["upper"],
                                                self.sim_game.throws["lower"], self.weight)

                        # if the node leads to a better board context, prune the remaining nodes of this subtree and
                        # return to outer layer
                        if _u_s > best_score:
                            best_score = _u_s
                            best_move = upp
                            self.sim_game.revert(_move, _battles, _throw)
                            break

                        self.sim_game.revert(_move, _battles, _throw)

            # lower handler
            else:
                # pruning: if the current move score is worse than the best already found, skip
                if l_s >= lyr_best:
                    lyr_best = l_s
                    best_move = loo
                else:
                    self.sim_game.revert(move, battles, throw)
                    continue

                # pruning: only expand moves where upper is "winning" over lower
                if u_s < l_s:
                    pack = product(
                        list(self.sim_game.available_actions("upper")),
                        list(self.sim_game.available_actions("lower"))
                    )
                    siz += len(list(pack))
                    for (_upp, _loo) in pack:
                        ct += 1
                        _snapshot, _throw, _battles, _move = self.sim_game.update(_upp, _loo)

                        _u_s, _l_s = evaluation(self.sim_game.board, self.sim_game.throws["upper"],
                                                self.sim_game.throws["lower"], self.weight)

                        # if the node leads to a better board context, prune the remaining nodes of this subtree and
                        # return to outer layer
                        if _l_s > best_score:
                            best_score = _l_s
                            best_move = loo
                            self.sim_game.revert(_move, _battles, _throw)
                            break

                        self.sim_game.revert(_move, _battles, _throw)

            # revert the simulated update
            self.sim_game.revert(move, battles, throw)

        if not best_move:
            if self.name == "upper":
                best_move = random.choice(upper_actions)
            else:
                best_move = random.choice(lower_actions)

        print("actual reached="+str(ct)+" ;expected="+str(siz))
        return best_move

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

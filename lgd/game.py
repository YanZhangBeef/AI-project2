"""
A reduced version of referee.game that simulates operation for one turn.
Does not actually "play" and does not output any log information.
"""

import sys
import time
import logging
import collections
from copy import copy,deepcopy

from referee.log import comment

# all hexes
_HEX_RANGE = range(-4, +4 + 1)
_ORD_HEXES = [
    (r, q) for r in _HEX_RANGE for q in _HEX_RANGE if -r - q in _HEX_RANGE
]
_SET_HEXES = frozenset(_ORD_HEXES)

# nearby hexes
_HEX_STEPS = [(1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1)]


def _ADJACENT(x):
    rx, qx = x
    return _SET_HEXES & {(rx + ry, qx + qy) for ry, qy in _HEX_STEPS}


# rock-paper-scissors mechanic
_BEATS_WHAT = {"r": "s", "p": "r", "s": "p"}
_WHAT_BEATS = {"r": "p", "p": "s", "s": "r"}


def battle(symbols):
    types = {s.lower() for s in symbols}
    if len(types) == 1:
        # no fights
        return symbols
    if len(types) == 3:
        # everyone dies
        return []
    # else there are two, only some die:
    for t in types:
        # those who are not defeated stay
        symbols = [s for s in symbols if s.lower() != _BEATS_WHAT[t]]
    return symbols


# draw conditions
_MAX_TURNS = 360  # per player


class IllegalActionException(Exception):
    """If this action is illegal based on the current board state."""




class Game:
    """
    Represent the evolving state of a game. Main useful methods
    are __init__, update, over, end, and __str__.
    """

    def __init__(self):
        # initialise game board state, and both players with zero throws
        self.board = dict()
        self.throws = {"upper": 0, "lower": 0}

        self.to_revert_battle = dict()
        self.to_revert_move = []
        self.to_revert_throw = []


        # also keep track of some other state variables for win/draw
        # detection (number of turns, state history)
        self.nturns = 0
        self.result = None

    def update(self, upper_action, lower_action):
        """
        Submit an action to the game for validation and application.
        If the action is not allowed, raise an InvalidActionException with
        a message describing allowed actions.
        Otherwise, apply the action to the game state.
        """
        # no need of validation - input is chosen from available actions
        self.to_revert_battle = dict()
        self.to_revert_move = []
        self.to_revert_throw = []
        battles = []
        atype, *aargs = upper_action

        if atype == "THROW":
            s, x = aargs
            self.to_revert_throw.append([s.upper(), x])
            if x not in self.board:
                self.board[x] = [s.upper()]
            else:
                self.board[x].append(s.upper())
            self.throws["upper"] += 1
            battles.append(x)
        else:
            x, y = aargs
            # remove ONE UPPER-CASE SYMBOL from self.board[x] (all the same)
            s = self.board[x][0].upper()
            self.to_revert_move.append([x, y, s])
            self.board[x].remove(s)
            if not self.board[x]:
                del self.board[x]
            if y not in self.board:
                self.board[y] = [s]
            else:
                self.board[y].append(s)
            # add it to self.board[y]
            battles.append(y)

        atype, *aargs = lower_action
        if atype == "THROW":
            s, x = aargs
            self.to_revert_throw.append([s.lower(), x])
            if x not in self.board:
                self.board[x] = [s.lower()]
            else:
                self.board[x].append(s.lower())
            self.throws["lower"] += 1
            battles.append(x)
        else:
            x, y = aargs
            # remove ONE LOWER-CASE SYMBOL from self.board[x] (all the same)
            s = self.board[x][0].lower()
            self.to_revert_move.append([x, y, s])
            self.board[x].remove(s)
            if not self.board[x]:
                del self.board[x]
            if y not in self.board:
                self.board[y] = [s]
            else:
                self.board[y].append(s)
            # add it to self.board[y]
            battles.append(y)
        # resolve hexes with new tokens:
        for x in battles:
            if x not in self.board:
                continue

            temp = self.board[x]
            self.board[x] = battle(self.board[x])

            if self.board[x] != temp:
                self.to_revert_battle[x] = temp
            if not self.board[x]:
                del self.board[x]

        return self.snap(self.board), self.to_revert_throw, self.to_revert_battle, self.to_revert_move

    def avoid(self, action, side):
        """
        avoid obviously no good steps
        1) suicide moves
        2) kills teammate who is not stacking with an opponent
        3) TBD
        """
        atype, *aargs = action

        if atype == "THROW":
            s, x = aargs
            if _WHAT_BEATS[s.lower()] in [p.lower() for p in self.board[x]]:
                return True
            if side == "upper":
                if _BEATS_WHAT[s.lower()].upper() in self.board[x] and _BEATS_WHAT[s.lower()] not in self.board[x]:
                    return True

            else:
                if _BEATS_WHAT[s.lower()] in self.board[x] and _BEATS_WHAT[s.lower()].upper() not in self.board[x]:
                    return True

        else:
            x, y = aargs
            s = self.board[x][0]
            if side == "upper":
                if _BEATS_WHAT[s.lower()].upper() in self.board[y] and _BEATS_WHAT[s.lower()] not in self.board[y]:
                    return True
            else:
                if _BEATS_WHAT[s.lower()] in self.board[y] and _BEATS_WHAT[s.lower()].upper() not in self.board[y]:
                    return True

        return False

    def revert(self, move, battles, throw):
        if battles:
            for key, val in battles.items():
                self.board[key] = val

        if throw:
            for [s, y] in throw:
                self.board[y].remove(s)
                if not self.board[y]:
                    del self.board[y]

                if s.isupper():
                    self.throws["upper"] -= 1
                elif s.islower():
                    self.throws["lower"] -= 1


        if move:
            for [x, y, s] in move:
                self.board[y].remove(s)
                if not self.board[y]:
                    del self.board[y]
                if x not in self.board:
                    self.board[x] = [s]
                else:
                    self.board[x].append(s)


    def available_actions(self, colour):
        """
        A generator of currently-available actions for a particular player
        (assists validation).
        """
        throws = self.throws[colour]
        isplayer = str.islower if colour == "lower" else str.isupper
        if throws < 9:
            sign = -1 if colour == "lower" else 1
            throw_zone = (
                (r, q) for r, q in _SET_HEXES if sign * r >= 4 - throws
            )
            for x in throw_zone:
                for s in "rps":
                    yield "THROW", s, x
        occupied = {x for x, s in self.board.items() if any(map(isplayer, s))}
        for x in occupied:
            adjacent_x = _ADJACENT(x)
            for y in adjacent_x:
                yield "SLIDE", x, y
                if y in occupied:
                    opposite_y = _ADJACENT(y) - adjacent_x - {x}
                    for z in opposite_y:
                        yield "SWING", x, z

    def turn_detect_end(self, state):
        """
        Register that a turn has passed: Update turn counts and detect
        termination conditions.
        """
        # register turn
        self.nturns += 1

        # analyse remaining tokens
        up_throws = 9 - self.throws["upper"]
        up_tokens = [
            s.lower() for x in self.board.values() for s in x if s.isupper()
        ]
        up_symset = set(up_tokens)
        lo_throws = 9 - self.throws["lower"]
        lo_tokens = [
            s for x in self.board.values() for s in x if s.islower()
        ]
        lo_symset = set(lo_tokens)
        up_invinc = [
            s for s in up_symset
            if (lo_throws == 0) and (_WHAT_BEATS[s] not in lo_symset)
        ]
        lo_invinc = [
            s for s in lo_symset
            if (up_throws == 0) and (_WHAT_BEATS[s] not in up_symset)
        ]
        up_notoks = (up_throws == 0) and (len(up_tokens) == 0)
        lo_notoks = (lo_throws == 0) and (len(lo_tokens) == 0)
        up_onetok = (up_throws == 0) and (len(up_tokens) == 1)
        lo_onetok = (lo_throws == 0) and (len(lo_tokens) == 1)

        # condition 1: one player has no remaining throws or tokens
        if up_notoks and lo_notoks:
            self.result = "draw: no remaining tokens or throws"
            return
        if up_notoks:
            self.result = "winner: lower"
            return
        if lo_notoks:
            self.result = "winner: upper"
            return

        # condition 2: both players have an invincible token
        if up_invinc and lo_invinc:
            self.result = "draw: both players have an invincible token"
            return

        # condition 3: one player has an invincible token, the other has
        #              only one token remaining (not invincible by 2)
        if up_invinc and lo_onetok:
            self.result = "winner: upper"
            return
        if lo_invinc and up_onetok:
            self.result = "winner: lower"
            return

        # # condition 4: the same state has occurred for a 3rd time
        # if self.history[state] >= 3:
        #     self.result = "draw: same game state occurred for 3rd time"
        #     return

        # condition 5: the players have had their 360th turn without end
        if self.nturns >= _MAX_TURNS:
            self.result = "draw: maximum number of turns reached"
            return

        # no conditions met, game continues
        return

    def over(self):
        """
        True iff the game has terminated.
        """
        return self.result is not None

    def snap(self, what):
        """
        returns a snapshot of current image
        """
        return (
            # same symbols/players tokens in the same positions
            tuple(
                (x, tuple(sorted(ts))) for x, ts in what.items() if ts
            ),
            # with the same number of throws remaining for each player
            self.throws["upper"],
            self.throws["lower"],
        )

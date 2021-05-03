import numpy as np
import random
HEX_RANGE = range(-4, +4+1)
BOARD = [(r, q) for r in HEX_RANGE for q in HEX_RANGE if -r - q in HEX_RANGE]
set_board = frozenset(BOARD)
STEPS = [(1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1)]
BEATS_WHAT = {"r": "s", "p": "r", "s": "p"}
WHAT_BEATS = {"r": "p", "p": "s", "s": "r"}
def ADJACENT(x):
    rx, qx = x
    return set_board & {(rx + ry, qx + qy) for ry, qy in STEPS}


"""
a state should contains:
1. where are thoese tokens with respect to lover and upper
2. The tokens that havent been placed on board
"""
class State:
    def __init__(self):
        self.throws = {"upper": 0, "lower": 0}
        self.board = {x: [] for x in BOARD}
    

    def available_actions(self, colour,opponent_flag):
        # opponent_flag = 1:self, = -1, opponent
        sign = -1 if colour == "lower" else 1
        sign = sign * opponent_flag
        target_colour = "upper" if sign == 1 else "lower"
        isplayer = str.islower if target_colour == "lower" else str.isupper
        #code here are copied directely from
        throws = self.throws[target_colour]
        isplayer = str.islower if target_colour == "lower" else str.isupper
        if throws < 9:
            sign = -1 if target_colour == "lower" else 1
            throw_zone = (
               (r, q) for r, q in self.board if sign * r >= 4 - throws
            )
            for x in throw_zone:
                for s in "rps":
                    yield "THROW", s, x
        occupied = {x for x, s in self.board.items() if any(map(isplayer, s))}
        for x in occupied:
            adjacent_x = ADJACENT(x)
            for y in adjacent_x:
                yield "SLIDE", x, y
                if y in occupied:
                    opposite_y = ADJACENT(y) - adjacent_x - {x}
                    for z in opposite_y:
                        yield "SWING", x, z
    
    def update_state(self, opponenet_actions, player_action, colour):
        if colour == "lower" :
            upper_action = opponenet_actions
            lower_action = player_action
        else:
            lower_action = opponenet_actions
            upper_action = player_action
        
        battles = set()

        atype, *aargs = upper_action
        if atype == "THROW":
            s, x = aargs
            self.board[x].append(s.upper())
            self.throws["upper"] += 1
            battles.add(x)
            token = s
        else:
            x, y = aargs
            # remove ONE UPPER-CASE SYMBOL from self.board[x] (all the same)
            s = self.board[x][0].upper()
            self.board[x].remove(s)
            self.board[y].append(s)
                # add it to self.board[y]
            battles.add(y)
            token = s
        upper_movement = (token, upper_action)


        atype, *aargs = lower_action
        if atype == "THROW":
            s, x = aargs
            self.board[x].append(s.lower())
            self.throws["lower"] += 1
            battles.add(x)
            token = s
        else:
            x, y = aargs
            # remove ONE LOWER-CASE SYMBOL from self.board[x] (all the same)
            s = self.board[x][0].lower()
            self.board[x].remove(s)
            self.board[y].append(s)
            # add it to self.board[y]
            battles.add(y)
            token = s
        # resolve hexes with new tokens:
        defeateds = []
        lower_movement =  (token, lower_action)
        for x in battles:
            defeated, self.board[x] = BATTLE(self.board[x])
            defeateds.append((x,defeated))
        return (upper_movement, lower_movement), defeateds
    


    def Backtracking(self, actions, defeateds):
        upper_movement, lower_movement = actions
        upper_token, upper_action = upper_movement
        lower_token, lower_action = lower_movement
        #putting whatever was removed back to the board
        if defeateds != []:
            for coordinate, defeated in defeateds:
                for defeat_token in defeated:
                    self.board[coordinate].append(defeat_token)
        # undo the movements
        atype, *aargs = lower_action
        if atype == "THROW":
            s, x = aargs
            self.board[x].remove(s.lower())
            self.throws["lower"] -= 1
        else:
            x, y = aargs
            s = lower_token.lower()
            self.board[y].remove(s)
            self.board[x].append(s)

        atype, *aargs = upper_action
        if atype == "THROW":
            s, x = aargs
            self.board[x].remove(s.upper())
            self.throws["upper"] -= 1
        else:
            x, y = aargs
            s = upper_token.upper()
            self.board[y].remove(s)
            self.board[x].append(s)
    

    def evaluation(self, defeateds,colour):
        upper, lower = self.process_a_board()
        upper_score = 0
        lower_score = 0
        ud, ld= self.calculating_distance(upper,lower)
        #the distance between each individual token to its beatwut
        ud = my_sum(ud)
        ld = my_sum(ld) 
        #diversity of the token(throw an beat wut if there is no any)
        throw = 0
        
        #numb of tokens
        nou =  (9  - self.throws["upper"]) + len(upper["s"])+ len(upper["p"])+ len(upper["r"])
        nol = (9 - self.throws["lower"]) + len(lower["s"])+ len(lower["p"])+ len(lower["r"])
        #throws in the higher round is more valuable +
        #which one to thorw?: with least opponent:

        #summing up all the determinators
        upper_score = ud + nou
        lower_score = ld + nol
        if(colour == "upper"):
            return upper_score - lower_score
        return lower_score - upper_score
    def cunting_kill_and_die(self,defeateds):
        lower = 0
        upper = 0
        for coordinate, defeated in defeateds:
            for defeat_token in defeated:
                if(defeat_token.islower()):
                    lower +=1
                else:
                    upper += 1
        return lower,upper
    
    def calculating_distance(self,player,opponent):
        target_distance = []
        whatbeat_distance = []
        for pkey in "rps":
            beatwut = BEATS_WHAT[pkey]
            wubeat = WHAT_BEATS[pkey]    
            for pcoordinate in player[pkey]:
                for token in opponent[beatwut]:
                    target_distance.append(manhattan_distance(pcoordinate,token))
                for token in opponent[wubeat]:
                    whatbeat_distance.append(manhattan_distance(pcoordinate,token))
        return target_distance, whatbeat_distance
    

    def process_a_board(self):
        upper_tokens = {"s" : [], "p" : [], "r" : []}
        lower_tokens = {"s" : [], "p" : [], "r" : []}
        for x, s in self.board.items():
            for y in s:
                if y.islower():
                    lower_tokens[y].append(x)
                else:
                    upper_tokens[y.lower()].append(x)
        return upper_tokens, lower_tokens

def manhattan_distance(a,b):
    ax , ay = a
    bx, by = b
    return (abs(ax- bx) + abs(ay - by) + abs(ax + ay - bx - by))/2
        
def euclidean_distance(a,b):
    ax , ay =  a
    bx, by = b
    return np.sqrt(np.power(bx - ax,2) + np.power(by - ay,2) )
def my_sum(ls):
    re = 0
    for l in ls:
        # x = x +2/(e^x), closer have a higher weight.
        re = re + 2/np.power(2.71,l)
    return re    
def BATTLE(symbols):
    types = {s.lower() for s in symbols}
    length = len(types)
    if length == 1:
        # no fights
        return [], symbols
    if length == 3:
        # everyone dies
        return symbols, []
    # else there are two, only some die:
    first = types.pop()
    second = types.pop()
    #target = what is left
    target = first
    if (second != BEATS_WHAT[first]):
        target = second
    alived = []
    died = []
    for s in symbols:
        if s.lower() == target:
            alived.append(s)
        else:
            died.append(s)
    return died, alived


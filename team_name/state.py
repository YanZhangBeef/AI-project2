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
    

    def evaluation(self, colour):
        upper, lower = self.process_a_board()
        
        #d: distance to target; rt: remaing throw. no: number of token; ui: invicible tokens    
        ud,ld,rtu,rtl,nou,nol,ui,li = feature_selection(upper,lower,self.throws)
        opponent, inv = ("upper", ui) if colour == "lower" else ("lower", li)        
        upper_score = 12*ud + (3*nou + 6*rtu) + 3*ui 
        lower_score = 12*ld + (3*nol + 6*rtl) + 3*li
        #avoid the opponent has a invincible token
        #or you can call it the termination test
        
        if(self.throws[colour] >= 7 and self.throws[opponent] > self.throws[colour]):        
            if(self.throws[opponent] >= 8):
                if self.throws[colour] - self.throws[opponent] > inv:
                    return -999                      
        if(colour == "upper"):
            return upper_score - lower_score
        return lower_score - upper_score
    

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
        
def my_sum(ls):
    #return 2/np.power(2.73,0.4*ls)
    return 1/(ls+1.1)
def calculating_distance(player,opponent):
    maximum_target_distance = -1
    maximum_wutbeat_disatnce = -1
    for pkey in "rps":
        beatwut = BEATS_WHAT[pkey]
        wubeat = WHAT_BEATS[pkey]

        for pcoordinate in player[pkey]:
            total_sum = 0
            for token in opponent[beatwut]:
                total_sum = total_sum + my_sum(manhattan_distance(pcoordinate,token))
            if(total_sum > maximum_target_distance):
                maximum_target_distance = total_sum
            
            total_sum = 0
            for token in opponent[wubeat]:
                 total_sum = total_sum + my_sum(manhattan_distance(pcoordinate,token))
            if(total_sum > maximum_wutbeat_disatnce):
                maximum_wutbeat_disatnce = total_sum    
    return maximum_target_distance, maximum_wutbeat_disatnce

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

def token_weight(nb_opponent,opponent_tokens_on_board,remaining_throw):
    if  (opponent_tokens_on_board + remaining_throw == 0):
        return 9999#wining state
    return (nb_opponent + remaining_throw/3)/ (opponent_tokens_on_board + remaining_throw)

def feature_selection(upper, lower, throws):
    #distance
    ud, ld= calculating_distance(upper,lower)
    #remaining throw
    rtu = (9  - throws["upper"])
    rtl = (9 - throws["lower"])
    #tokens on board
    nou =  len(upper["s"])+ len(upper["p"])+ len(upper["r"])
    nol =  len(lower["s"])+ len(lower["p"])+ len(lower["r"])  
    #number of tokens (weighted) of each kind of token:
    weighted_upper = 0
    weighted_lower = 0

    for g in "rps":
        beatwut = BEATS_WHAT[g]
        if nou == 0:
            weighted_upper += 999
        else:
            weighted_upper += (len(upper[g])/nou) * token_weight(len(lower[beatwut]),nol,rtl)
        if nol == 0:
            weighted_lower += 999
        else:
            weighted_lower += (len(lower[g])/nol) *  token_weight(len(upper[beatwut]),nou,rtu)

    nou = weighted_upper
    nol = weighted_lower        
    #have a tokens that do not has a wutbeat
    upper_inv = 0
    lower_inv = 0
    for role in "spr":
        # there is a lower token that is inv
        if(len(lower[role]) > 0 and len(upper[WHAT_BEATS[role]]) == 0):
            lower_inv += 1
        if(len(upper[role]) > 0 and len(lower[WHAT_BEATS[role]]) == 0):
            upper_inv +=1
    
    # return all the features:
    return ud,ld,rtu,rtl,nou,nol,upper_inv,lower_inv

def machine_learning(colour):
    files = []
    x_train = np.array([])
    y_train = np.test([])
    
    #loading state.
    for f in files:
        with open(f) as file:
            data = json.load(file)
            upper = {"s" : [], "p" : [], "r" : []}
            lower = {"s" : [], "p" : [], "r" : []}
            self.throws = {"upper": 0, "lower": 0}  
            for i in data['upper']:
                upper_token[i[0]] = tuple((i[1],i[2]))
            for i in data['lower']:
                lower_token[i[0]] = tuple((i[1],i[2]))
            for i in data['throw']:
                lower_token[i[0]] = (i[1])    
            utility_score = data['utility'][0]
            ud,ld,rtu,rtl,nou,nol = feature_selection(upper,lower,colour)
            x_train.add(np.array([ud,ld,r·tu,rtl,nou,nol]))
            y_train.add(np.array[utility_score])
    # feeding the linear model and finding the best weight for eatch features:

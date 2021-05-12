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
                for s in random.choice(["prs","rsp","psr","rps","prs","psr"]):
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
    

    def evaluation(self, colour,defeateds,actions):
        upper, lower = self.process_a_board()

        #d: distance to target; rt: remaing throw. no: number of token; ui: invicible tokens    
        ud,ld,rtu,rtl,nou,nol,ui,li,wu,wl = feature_selection(upper,lower,self.throws)
        opponent, inv = ("upper", ui) if colour == "lower" else ("lower", li)        
        upper_score = 8*ud + 12*(nou) + (9-rtl) * ui + rtu
        lower_score = 8*ld + 12*(nol) + (9-rtu) * li + rtl
        #avoid the opponent has a invincible token
        #or you can call it the termination test
        if(self.throws[colour] >= 7 and self.throws[opponent] > self.throws[colour]):        
            if(self.throws[opponent] >= 8):
                if self.throws[colour] - self.throws[opponent] > inv:
                    return -999                     
        
        if(colour == "upper"):
            #return upper_score-lower_score
            
            return 8*ud + 12*(nou) + 2*(rtu - rtl)+ wu - 18*(nol)-4*ld-li-wl
        #return lower_score - upper_score
        return 8*ld + 12*(nol) + 2*(rtl - rtu) + wl - 18*(nou)-4*ud -ui-wu

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
    return 1/(ls+0.001)-0.001

def calculating_distance(upper,lower):
    UtoL = 0
    LtoU = 0
    for key in "rps":
        beatwut = BEATS_WHAT[key]
        Max_UtoL = 0
        for ucoordinate in upper[key]:
            token_distance = 0
            for lcoordinate in lower[beatwut]:
                token_distance += my_sum(manhattan_distance(ucoordinate,lcoordinate))
            if token_distance > Max_UtoL:
                 Max_UtoL = token_distance
        
        Max_LtoU = 0 
        for lcoordinate in lower[key]:
            token_distance = 0
            for ucoordinate in upper[beatwut]:
                token_distance += my_sum(manhattan_distance(ucoordinate,lcoordinate))
            if token_distance > Max_LtoU:
                Max_LtoU = token_distance
        UtoL += Max_UtoL
        LtoU += Max_LtoU
    return UtoL,LtoU

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
            weighted_upper -= 40
        else:
            weighted_upper += (len(upper[g])/nou) * token_weight(len(lower[beatwut]),nol,rtl)
        if nol == 0:
            weighted_lower -= 40
        else:
            weighted_lower += (len(lower[g])/nol) *  token_weight(len(upper[beatwut]),nou,rtu)
    wu = weighted_upper
    wl = weighted_lower       
    #have a tokens that do not has a wutbeat
    upper_inv = 0
    lower_inv = 0
    for role in "spr":
        # there is a lower token that is inv
        if(len(lower[role]) > 0 and len(upper[WHAT_BEATS[role]]) == 0):
            lower_inv += 1

        if(len(upper[role]) > 0 and len(lower[WHAT_BEATS[role]]) == 0):
            upper_inv +=1
    nou = nou + rtu
    nol = nol + rtl
    # return all the features:
    return ud,ld,rtu,rtl,nou,nol,upper_inv,lower_inv,wu,wl
##################### REPORT SOURCE CODE########################
###MACHINE LEARNING PART###
"""
def machine_learning(colour):
    #import numpy as np
    #from sklearn.linear_model import LinearRegression
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
            y_train.add(utility_score)
    # feeding the linear model and finding the best weight for eatch features:
    regr = linear_model.LinearRegression()
    regr.fit(x_train, y_train)
    return regr.coef

"""
##heursistic deepning(recusive)###
def throw_zone_size(n):
    if n > 4:
        return throw_zone_size(8-4) + throw_zone_size(4)
    elif n == 0:
        return 5
    else:
        return 5 + 1 + throw_zone_size(n-1)
    

"""

Global_max = -inf
Global_max_action = None
def heursistic_get_depth(state):
    throw =  state.throw[upper]* state.throw[lower]
    upper_token, lower_token = process_a_board(state.board)
    upper_length = 0
    lower_length = 0
    for l in "rps":
        upper_length += len(upper_token[l])
        lower_length += len(lower_token[l])
    possible_state_without_pruning = (state.throw["upper"] + upper_length)\
    * (lower_length * state.throw["lower"])
    #a^b = c; loga(C)= B
    #
    suitable_depth = (2*np.log(possible_state_whithout_pruning, 100000)).floor()
    best_action = recusiveminimax(state,suitable_depth,current_depth)
    return best_action



def recusiveminimax(state,wanted_depth, current_depth):
    if wanted_depth == current_depth:
        return state.evaluate()

    local_min = inf
    for player_action in player_actions:
        for opponent_action in opponent_actions:
            newstate = deepcopy(state)
            state.update(player_action,lower_action)
            current_score = recusiveminimax(wanted_depth,current_depth+1,newstate)
            if current_score <= Global_max:
                #this will be pass to the fist layer then it knows its time to run a-b pruning
                return current_score
            elif(current_score> local_min):
                local_min = current_score
                if(current_depth == 1):
                    Global_max_action = player_action
    Global_max = local_min# update the global max
    return maximum #passing the utility score to the layer above
"""
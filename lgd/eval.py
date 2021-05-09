

def axial_to_cube(axial):
    x = axial[0]
    z = axial[1]
    y = -x-z
    return [x, y, z]

def cube_distance(a, b):
    a0,a1,a2 = axial_to_cube(a)
    b0,b1,b2 = axial_to_cube(b)
    return (abs(a0 - b0) + abs(a1 - b1) + abs(a2 - b2)) / 2


def evaluation(Board,upper_throw,lower_throw,weight):
    up_score = 0
    low_score = 0
    UP, LOW, token_dict = process_board(Board)
    w_counter_num,w_zero_num,w_duplicate_num,w_throw_left = weight
    #print(token_dict)
    up_d_score, low_d_score = diversity_count(token_dict,w_zero_num,w_duplicate_num)
    counter_up, counter_low = counter_num(UP, LOW)
    up_score = w_counter_num*counter_up + w_throw_left*throw_left_eval(upper_throw) + up_d_score
    low_score = w_counter_num*counter_low + w_throw_left*throw_left_eval(lower_throw) + low_d_score
    up_final_score = (low_score) / (up_score + low_score + 0.0000001)
    low_final_score = (up_score) / (up_score + low_score + 0.0000001)
    return up_final_score, low_final_score


def diversity_count(token_dict,w_zero_num,w_duplicate_num):
    count_list = []
    for value in token_dict.values():
        count_list.append(value)
    up_score = 0
    low_score = 0
    up_count_list = count_list[0:2]
    low_count_list = count_list[3:5]
    up_zero_num = up_count_list.count(0)
    low_zero_num = low_count_list.count(0)
    if up_zero_num == 3 or up_zero_num == 2:
        up_score = 60
    elif up_zero_num == 1:
        up_score = 30
    else:
        up_score = 0
    if low_zero_num == 3 or low_zero_num == 2:
        low_score = 60
    elif low_zero_num == 1:
        low_score = 30
    else:
        low_score = 0
    w_duplicate_num
    up_duplicate_score = 0
    low_duplicate_score = 0
    for i in up_count_list:
        if i == 3:
            up_duplicate_score = up_duplicate_score + 10
        elif i == 4:
            up_duplicate_score = up_duplicate_score + 30
        elif i >= 5:
            up_duplicate_scoreup_duplicate_score = up_duplicate_score + 200
    for i in low_count_list:
        if i == 3:
            low_duplicate_score = low_duplicate_score + 10
        elif i == 4:
            low_duplicate_score = low_duplicate_score + 30
        elif i >= 5:
            low_duplicate_score = low_duplicate_score + 200
    up_score = up_score*w_zero_num + up_duplicate_score*w_duplicate_num
    low_score = low_score*w_zero_num + low_duplicate_score*w_duplicate_num
    return up_score, low_score



def throw_left_eval(throw):
    if throw == 0:
        return 60
    elif throw == 1:
        return 45
    elif throw == 2:
        return 36
    elif throw == 3:
        return 30
    elif throw == 4:
        return 24
    elif throw == 5:
        return 18
    elif throw == 6:
        return 12
    elif throw == 7:
        return 6
    elif throw == 8:
        return 3
    else:
        return 0


def process_board(Board):
    UP = []
    LOW = []
    token_dict = {"R": 0, "S": 0, "P": 0, "r": 0, "s": 0, "p": 0}
    for loc in Board.keys():
        for piece in Board[loc]:
            if piece in ("R", "S", "P"):
                UP.append((loc, piece, "U"))
            else:
                LOW.append((loc, piece, "L"))
            token_dict[piece] = token_dict[piece] + 1
    return UP, LOW, token_dict

def counter_distance_score(loc1, loc2):
    distance = cube_distance(loc1, loc2)
    if distance == 0:
        return 18
    elif distance == 1:
        return 15
    elif distance == 2:
        return 10
    elif distance == 3:
        return 8
    elif distance == 4:
        return 6
    elif distance == 5:
        return 4
    elif distance == 6:
        return 3
    elif distance == 7:
        return 2
    elif distance == 8:
        return 1
    else:
        return 0


def counter_num(UP, LOW):
    counter_up = 0
    counter_low = 0
    for piece_u in UP:
        if piece_u[1] == "R":
            for piece_l in LOW:
                if piece_l[1] == "p":
                    counter_up = counter_up + counter_distance_score(piece_u[0], piece_l[0])
        elif piece_u[1] == "S":
            for piece_l in LOW:
                if piece_l[1] == "r":
                    counter_up = counter_up + counter_distance_score(piece_u[0], piece_l[0])
        else:
            for piece_l in LOW:
                if piece_l[1] == "s":
                    counter_up = counter_up + counter_distance_score(piece_u[0], piece_l[0])
    for piece_l in LOW:
        if piece_l[1] == "r":
            for piece_u in UP:
                if piece_u[1] == "P":
                    counter_low = counter_low + counter_distance_score(piece_u[0], piece_l[0])
        elif piece_l[1] == "s":
            for piece_u in UP:
                if piece_u[1] == "R":
                    counter_low = counter_low + counter_distance_score(piece_u[0], piece_l[0])
        else:
            for piece_u in UP:
                if piece_u[1] == "S":
                    counter_low = counter_low + counter_distance_score(piece_u[0], piece_l[0])

    return counter_up, counter_low

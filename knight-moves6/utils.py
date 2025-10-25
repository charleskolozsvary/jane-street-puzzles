"""Use camel case for functions, and use underscores for variable names"""

GRID_LETTERS = [['A', 'A', 'A', 'A', 'A', 'A'],
                ['A', 'A', 'A', 'A', 'B', 'B'],
                ['A', 'A', 'B', 'B', 'B', 'B'],
                ['B', 'B', 'B', 'B', 'C', 'C'],
                ['B', 'B', 'C', 'C', 'C', 'C'],
                ['C', 'C', 'C', 'C', 'C', 'C']]
L_MOVES = [(1, 2), (-1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, 1), (-2, -1)]
INDEX_TO_CHESS_LETTER = {0:'a', 1:'b', 2:'c', 3:'d', 4:'e', 5:'f'}
CHESS_LETTER_TO_INDEX = dict((v, k) for k, v in INDEX_TO_CHESS_LETTER.items())
GRID_SIZE = 6

def chessFormat(trip):
    chess_str = ""
    for position in trip:
        chess_str += INDEX_TO_CHESS_LETTER[position[0]]+str(position[1]+1)+","
    return chess_str[:-1]

def letterOfPosition(position):
    return GRID_LETTERS[position[0]][position[1]]

def outOfBounds(position):
    return position[0] < 0 or position[0] >= GRID_SIZE or position[1] < 0 or position[1] >= GRID_SIZE
    
def add2D(x1, x2):
    return (x1[0] + x2[0], x1[1] + x2[1])

def neighbors(position, trip, letter_to_filter_by = None):
    neighs = []
    for move in L_MOVES:
        nei = add2D(move, position)
        if outOfBounds(nei) or nei in trip:
            continue
        if letter_to_filter_by != None and letter_to_filter_by != letterOfPosition(nei):
            continue
        neighs.append(nei)
    return neighs
    
def gridString(curr_position):
    leading_space = 2
    letter_space = 3
    grid_str = ""
    hline = "-"*(3*(GRID_SIZE+3)-2)+"\n"
    for y in range(GRID_SIZE-1, -1, -1):
        grid_str += f'{'':{leading_space}}{hline}{y+1} |'
        for x in range(GRID_SIZE):
            letter = letterOfPosition((x, y))
            grid_str += (f'{letter.lower():^{letter_space}}' if (x,y) != curr_position else f'*{letter}*')+"|"
        grid_str += "\n"
    grid_str += f'{'':{leading_space}}{hline}'
    letters_at_bottom = ''
    for letter in "abcdef":
        letters_at_bottom += f'{letter:^{letter_space}} '
    grid_str += f'{'':{leading_space+1}}{letters_at_bottom}\n'
    return grid_str
    
def verifySolution(solution, target_score):
    solution = solution.split(",")
    letter_values = [int(solution[0]), int(solution[1]), int(solution[2])]
    assert sorted(letter_values) == sorted(list(set(letter_values))), f'The positive integers assigned to A, B, and C are not distinct (letter_values = {str(sorted(letter_values))} ≠ {str(sorted(list(set(letter_values))))} = sorted(list(set(letter_values)))).'
    abc_values = {'A':letter_values[0],'B':letter_values[1],'C':letter_values[2]}
    trips = solution[3:]; chess_trips = trips.copy()
    for i in range(len(trips)):
        trips[i] = (CHESS_LETTER_TO_INDEX[trips[i][0]], int(trips[i][1])-1)
    trip_split_idx = trips.index((5,5))+1
    trip1 = trips[:trip_split_idx]; chess_trip1 = chess_trips[:trip_split_idx]
    trip2 = trips[trip_split_idx:]; chess_trip2 = chess_trips[trip_split_idx:]
    def verifySomeTripPositions(trip, start, end):
        assert trip[0] == start and trip[-1] == end and len(trip) == len(set(trip)), f'The trip begins at an invalid position ({trip[0]} ≠ {start}), or the trip ends at an invalid position ({trip[-1]} ≠ {end}), or there are repeated positions in the trip (len(trip) = {len(trip)} ≠ {len(set(trip))} = len(set(trip))).'
    verifySomeTripPositions(trip1, (0,0), (5,5))
    verifySomeTripPositions(trip2, (0,5), (5,0))
    def stepDisplay(position, chess_position, score, letter, arith_str, first_display = False, space = 6):
        display_str = ''
        if not first_display:
            display_str += f'{arith_str[0]:^{space}}\n{arith_str[1]:^{space}}\n\n{'|':^{space}}\n{'V':^{space}}\n\n'
        grid_str = gridString(position).split('\n')
        middle_display_row_idx = GRID_SIZE
        for i in range(middle_display_row_idx):
            display_str += f'{'':^{space*3}}'+grid_str[i]+'\n'
        display_str += f'{score:^{space}}{letter:^{space}}{chess_position:^{space}}'+grid_str[middle_display_row_idx]+'\n'
        for i in range(middle_display_row_idx+1, len(grid_str)):
            display_str += f'{'':^{space*3}}'+grid_str[i]+'\n'
        return display_str
    def canTravel(trip, chess_trip, trip_number = -1):
        score = abc_values['A']
        prev_position = trip[0]
        display_str = stepDisplay(trip[0], chess_trip[0], score, 'A', None, first_display = True)
        for i, position in enumerate(trip[1:]):
            prev_letter = letterOfPosition(prev_position)
            curr_letter = letterOfPosition(position)
            prev_letter_neighbors = neighbors(prev_position, trip[0:i+1], curr_letter)
            assert position in prev_letter_neighbors, f'{position} is not among {str(prev_letter_neighbors)}, the neighbors of the previous position that are also the same letter as the current position, {curr_letter}.'
            arith_string = None
            if prev_letter == curr_letter:
                score += abc_values[curr_letter]
                arith_string = [" + ", str(abc_values[curr_letter])]
            else:
                score *= abc_values[curr_letter]
                arith_string = [" * ", str(abc_values[curr_letter])]
            display_str += stepDisplay(position, chess_trip[i+1], score, curr_letter, arith_string)
            prev_position = position
        assert score == target_score, 'The score at the end of the trip was not equal to the target score (end score {score} ≠ {target_score} target score).'
        print(f'TRIP {trip_number}:\n'+display_str+'\n')
    print(f'A = {abc_values['A']:2},\nB = {abc_values['B']:2},\nC = {abc_values['C']:2}')
    canTravel(trip1, chess_trip1, trip_number = 1)
    canTravel(trip2, chess_trip2, trip_number = 2)

"""Create n multichoose k multisets from the list of objects; n is the number of objects. Source: https://github.com/ekg/multichoose"""    
def multichoose(k, objects):
    j,j_1,q = k,k,k  # init here for scoping
    r = len(objects) - 1
    a = [0 for i in range(k)] # initial multiset indexes
    while True:
        yield [objects[a[i]] for i in range(0,k)]  # emit result
        j = k - 1
        while j >= 0 and a[j] == r: j -= 1
        if j < 0: break  # check for end condition
        j_1 = j
        while j_1 <= k - 1:
            a[j_1] = a[j_1] + 1 # increment
            q = j_1
            while q < k - 1:
                a[q+1] = a[q] # shift left
                q += 1
            q += 1
            j_1 = q
            
def multiSetsToDicts(arrarr):
    dicts = []
    for arr in arrarr:
        dict = { }
        for elem in arr:
            if elem in dict:
                dict[elem] += 1
            else:
                dict[elem] = 1
        dicts.append(dict)
    return dicts

"""
Return a dictionary where the keys are the sums of A, B, and C (within the range sum_lower, sum_upper, inclusive) and the values are lists of dictionaries, each of which (the dictionaries) give the positive integers assigned to A, B, and C as values to the keys of the single character strings 'A', 'B', or 'C'.
"""    
def abcSumDict(abc_sum_lower, abc_sum_upper):
    abc_sum_dict = {}
    for k in range(abc_sum_lower, abc_sum_upper+1):
        abc_sum_dict[k] = multiSetsToDicts(list(multichoose(k, ['A', 'B', 'C'])))
    return abc_sum_dict

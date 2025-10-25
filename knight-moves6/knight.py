from utils import neighbors, chessFormat, letterOfPosition, verifySolution, abcSumDict
tot_recursive_calls = 0

def cornerToCornerTrip(depth, position, trip, score, max_depth, end_position, target_score, abc_values):
    global tot_recursive_calls
    tot_recursive_calls += 1
    if depth > max_depth or score > target_score or position in trip or end_position in trip:
        return
    trip.append(position)
    if score == target_score and position == end_position:
        raise Exception(chessFormat(trip))
    neighs = neighbors(position, trip)
    for nei in neighs:
        trip_copy = trip.copy()
        curr_letter = letterOfPosition(position)
        next_letter = letterOfPosition(nei)
        next_score = score + abc_values[curr_letter] if curr_letter == next_letter else score * abc_values[next_letter]
        cornerToCornerTrip(depth+1, nei, trip_copy, next_score, max_depth, end_position, target_score, abc_values)
        

def solve(max_depth, target_score, abc_sum_lower, abc_sum_upper):
    abc_sum_dict = abcSumDict(abc_sum_lower, abc_sum_upper)
    for abc_values in abc_sum_dict.values():
        for abc_v in abc_values:
            if len(abc_v.values()) != len(set(abc_v.values())) or 'A' not in abc_v or 'B' not in abc_v or 'C' not in abc_v:
                continue
            try:
                cornerToCornerTrip(0, (0,0), [], abc_v['A'], max_depth, (5,5), target_score, abc_v)
            except Exception as trip1:
                try:
                    cornerToCornerTrip(0, (0,5), [], abc_v['A'], max_depth, (5,0), target_score, abc_v)
                except Exception as trip2:
                    solution = f'{abc_v['A']},{abc_v['B']},{abc_v['C']},{trip1},{trip2}'
                    try:
                        verifySolution(solution, target_score)
                    except Exception as trip_invalid:
                        print('The solution was invalid. This should not happen, btw.', trip_invalid)
                    else:
                        print(f'Solution found.\n{solution}')
                        return
    print('A solution was not found. Perhaps abc_sum_upper < 6 or the max_depth was not large enough (try 14 =< max_depth < 20 for the lowest value of A + B + C = 6).')
    
if __name__ == '__main__':
    max_depth = 14
    target_score = 2024
    abc_sum_lower = 6
    abc_sum_upper = 49
    solve(max_depth, target_score, abc_sum_lower, abc_sum_upper)
    print(f'Total cornerToCornerTrip recursive calls: {tot_recursive_calls}')
    
    # Takes ~7 seconds to solve for A + B + C = 6.
    # As abc_sum_lower increases or max_depth decreases, solutions are found more quickly.

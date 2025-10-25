from permutations import permute

board = {
    (0, 0): 0,  (1, 0): 77, (2, 0): 32, (3, 0): 403, (4, 0): 337, (5, 0): 452,
    (0, 1): 5,  (1, 1): 23, (2, 1): -4, (3, 1): 592, (4, 1): 445, (5, 1): 620,
    (0, 2): -7, (1, 2): 2,  (2, 2): 357, (3, 2): 452, (4, 2): 317, (5, 2): 395,
    (0, 3): 186, (1, 3): 42, (2, 3): 195, (3, 3): 704, (4, 3): 452, (5, 3): 228,
    (0, 4): 81,  (1, 4): 123, (2, 4): 240, (3, 4): 443, (4, 4): 353, (5, 4): 508,
    (0, 5): 57,  (1, 5): 33, (2, 5): 132, (3, 5): 268, (4, 5): 492, (5, 5): 732
}

right = [1, 2, 6, 4]
up = [1, 3, 6, 5]
left = [1, 4, 6, 2]
down = [1, 5, 6, 3]

dimension = 6
dim = dimension - 1

directions = {
    (1, 0): right,
    (0, 1): up,
    (-1, 0): left,
    (0, -1): down
}


def trace_path(path, e_config):
    k = len(path)
    die = e_config.copy()
    for i in range(k - 1, 0, -1):
        delta = (path[i - 1][0] - path[i][0], path[i - 1][1] - path[i][1])
        die = permute(die, directions[delta])

    symbols = {(1, 0): '→', (0, 1): '↑', (-1, 0): '←', (0, -1): '↓'}
    mess = ['move', 'top face', 'coordinate', 'board value', 'next direction']
    print('starting configuration: ', die)
    print(f'{mess[0]:^4}|{mess[1]:^9}|{mess[2]:^10}|{mess[3]:^12}|{mess[4]:^14}')
    for i in range(0, k - 1):
        delta = (path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1])
        print(f'{i:^4} {str(die[0]):^9} {str(path[i]):^10} {str(board[path[i]]):^12} {symbols[delta]:^15}')
        die = permute(die, directions[delta])
    m2 = ['32', 'FINISHED']
    print(f'{m2[0]:^4} {str(die[0]):^9} {str(path[32]):^10} {str(board[path[32]]):^12} {m2[1]:^15}')

    b = board.copy()
    for p in path:
        if p not in b:
            continue
        del b[p]

    print('\n\nsquares not visited: ')
    for not_vis in b:
        print(f'{str(not_vis):^4}  {str(b[not_vis]):^7}')
    print('\n\nsum of values of squares not visited =', sum(b.values()))


def search(pos, die, score, move, path, max_depth):  # move is nth move -- a number
    if move >= max_depth:
        if pos == (5, 5):
            victory = 'VICTORY'
            print(f'{victory:^110}')
            trace_path(path, die)
        print(f'{str(pos):^20}{str(die):^70}{str(score):^20}')
        return

    dir_count = 0
    for d in directions:
        p = (pos[0] + d[0], pos[1] + d[1])  # temp pos
        if p[0] < 0 or p[1] < 0 or p[0] > dim or p[1] > dim:
            continue
        moved_die = permute(die, directions[d])
        m = move + 1
        top_face = moved_die[0]
        s = top_face * m + score
        b = board[p]
        if top_face == 0 or s == board[p]:
            new_path = path.copy()
            new_path.append(p)
            dir_count += 1
            if top_face == 0:
                moved_die[0] = (b - s) // m
                search(p, moved_die, b, m, new_path, max_depth)
            else:
                search(p, moved_die, s, m, new_path, max_depth)
                
    return


def search_rec(max_depth: int):
    default_die = [0 for i in range(0, dimension)]
    return search((0, 0), default_die, 0, 0, [(0, 0)], max_depth)

if __name__ == '__main__':
    for i in range(0, 33):
        search_rec(i)
        m = 'i = ' + str(i)
        print(f'{m:^110}\n')

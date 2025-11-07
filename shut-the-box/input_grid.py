def inputGrid(width: int):
    grid = {}
    out = 'grid = {\n'
    for y in range(width):
        for x in range(width):
            pos = (x, y)
            info = input('{}\n'.format(pos))
            if info == '': # e for empty
                continue
            elif info == 'f':
                out += "{}: '', ".format(pos)
            else:
                out += "{}: '{}', ".format(pos, info)
        out += '\n'
    out += '}\nprint(grid)'
    with open('written-grid.txt', 'w') as f:
        f.write(out)

if __name__ == '__main__':
    inputGrid(20)
            
            

import os
import polyominoes
from clues import CLUES

#=========================================================
# Write tikz commands using code from preamble-tikzify.txt
#=========================================================

def corners2paths(corners: list[str]) -> list[str]:
    
    def corner2path(d: int, bounds: dict[str, int], corner: str) -> str:
        horizontalSide, verticalSide = corner[0], corner[1]
        startPos = {'x': bounds[verticalSide], 'y': bounds[horizontalSide]}
        path = '\\drawthick ({},{})--++'.format(startPos['x'], startPos['y'])
        if corner == 'TL':
            path += '(0,1)--++({},0)--++(0,-1)--++({},0)--++(0,{})--++(-1,0)--cycle;'.format(d+1, -d, -d)
        elif corner == 'TR':
            path += '({},0)--++(0,1)--++({},0)--++(0,{})--++(-1,0)--cycle;'.format(-d, d+1, -(d+1))
        elif corner == 'BR':
            path += '({},0)--++(0,1)--++({},0)--++(0,{})--++(1,0)--++(0,{})--cycle;'.format(-d, d, d, -(d+1))
        elif corner == 'BL':
            path += '(0,{})--++(1,0)--++(0,{})--++({},0)--++(0,-1)--cycle;'.format(d+1, -d, d)
        else:
            assert False, "corner wasn't TL, TR, BR, or BL"
        return path

    depth = len(corners)
    bounds = {'L': 0, 'B': 0, 'T': depth, 'R': depth}
    paths = []
    for corner in corners:
        paths.append(corner2path(depth, bounds, corner))
        horizontalSide, verticalSide = corner[0], corner[1]
        bounds[horizontalSide] += 1 if horizontalSide == 'B' else -1
        bounds[verticalSide]   += 1 if verticalSide   == 'L' else -1
        depth -= 1
    return paths

#==========================================
# Writing and compiling the LaTeX code
#==========================================

def getTeXpreamble(fileName: str) -> str:
    with open(fileName, 'r') as readFH:
        return ''.join(readFH.readlines())

def compileTeX(body: str, noExtensionFileName: str) -> None:
    os.chdir('drawings/non-pdfs')
    texFile = '{}.tex'.format(noExtensionFileName)
    
    with open(texFile, 'w') as f:
        f.write(getTeXpreamble('../../preamble-tikzify.txt'))
        f.write(body)
        f.write('\n\\end{document}')
        
    os.system('pdflatex {}'.format(texFile))

    pdfFile = '{}.pdf'.format(noExtensionFileName)
    os.system('mv {} ..'.format(pdfFile))
    os.system('open ../{}'.format(pdfFile))
    
    os.chdir('../..')

def corners2tex(corners, hookGrid, perLine, clues, label= '', labelCoordinate = (0,0)):
    resizeWidth = (30 / perLine)-0.5
    tikzpicture = '\\resizebox{{{w}pc}}{{!}}{{\\begin{{tikzpicture}}\n'.format(w=resizeWidth)
    tikzpicture += '\n    '.join(corners2paths(corners))
    tikzpicture += '\\drawgriddotted{{{gridW}}}\n'.format(gridW=len(corners)+1)
    tikzpicture += clues
    if len(label.split('\n')) == 1:
        tikzpicture += '\\numbersquare{{{lab}}}{{{x}-.5}}{{{y}-.5}}\n'.format(lab=label, x=labelCoordinate[0], y=labelCoordinate[1])
    tikzpicture += '\\end{tikzpicture}}'
    return tikzpicture

def tupleArith(tup1, tup2, function):
    assert len(tup1) == len(tup2)
    return tuple([function(tup1[i], tup2[i]) for i in range(len(tup1))])

def drawClues(clues, partialGrid = None):
    commands = ''
    if clues is None:
        return commands
    add = lambda x, y: x + y
    scale = lambda x : -3*x/4
    def minus(tup: tuple[int]):
        return tuple([-t for t in tup])
    
    if partialGrid is None:
        for (x, y), digit in clues['filledsquares'].items():
            commands += '\\numbersquare{{{d}}}{{{x}}}{{{y}}}'.format(d=digit, x=x+1, y=y+1)
            
    for digit, coordinate in clues['digs'].items():
        movedir = tuple(map(scale, clues['digdirs'][coordinate]))
        (x, y) = tupleArith(movedir, coordinate, add)
        commands += '\\numbersquare{{{d}}}{{{x}}}{{{y}}}'.format(d=digit, x=x+1, y=y+1)
        
    for polyominoName, coordinate in clues['polys'].items():
        movedir = tuple(map(scale, clues['polydirs'][coordinate]))
        (x, y) = tupleArith(movedir, coordinate, add)
        commands += '\\numbersquare{{\\textcolor{{red}}{{{n}}}}}{{{x}}}{{{y}}}'.format(n=polyominoName, x=x+1, y=y+1)
    return commands

def drawHookPartitions(hookPartitions, perLine, labels, filename, maxDraw = None, validIdxs = []):
    if len(hookPartitions) == 0:
        print ('Nothing to draw...')
        return None
    
    dimension = len(hookPartitions[0]['hooks']['grid'])
    body = ''
    for i, hookpartition in enumerate(hookPartitions):
        if i % perLine == 0:
            body += '\n\\clearpage'
        if maxDraw is not None and i >= maxDraw:
            break
        labelcoor = ((len(hookpartition['hooks']['grid']) // 2) + 1, -1)
        lab = labels[i].split('\n')
        body += corners2tex(hookpartition['corners'], hookpartition['hooks']['grid'], perLine, drawClues(CLUES[dimension]), labels[i], labelcoor)
        if len(lab) == 2:
            body += '\n\\vspace{1pc}\\noindent'
            body += '{{\\large \\texttt{{{l0}}}}}'.format(l0 = lab[0])
            body += '\n\n\\medskip\\noindent'
            body += '{{\\large \\texttt{{{l1}}}}}'.format(l1 = lab[1])
            body += '\n'
            continue
        body += '\\,'
    body += '\n\n\\Large\\noindent \\textsc{Valid Idxs}:\n\n'
    for vidx in validIdxs:
        body += '\\texttt{{{}}}\n\n'.format(vidx+1)
    compileTeX(body, filename)

def colorPolyominoes(polyominopartition):
    tikzCommands = ''
    for polyname, placement in polyominopartition.items():
        for (x, y) in placement:
            tikzCommands += '\\colorsquare{{{}}}{{{}}}{{{}}}'.format(polyname, x+1, y+1)
        tikzCommands += '\n'
    return tikzCommands

def cover2tex(gridW: int, polyominoes: dict[str, list[tuple[int]]], perLine: int, label: str, clues):
    width = (30 / perLine)-.5
    labelcoor = (gridW // 2 + .5, -1)
    (x, y) = labelcoor
    return '''\\resizebox{{{w}pc}}{{!}}{{\\begin{{tikzpicture}}
    {colorCommands}
    {cls}
    \\drawgridthin{{{size}}}
    %\\draw ({x}, {y}) node {{\\LARGE {lab1}}};
    \\end{{tikzpicture}}}}'''.format(w=width, colorCommands = colorPolyominoes(polyominoes), size=gridW, lab1 = label, cls=drawClues(clues), x=x, y=y)

def drawCovers(gridW, covers, filename, perLine = 1, maxDraw: int = None):
    body = ''
    dimension = gridW
    clues = CLUES[dimension] if dimension in CLUES else None
    for i, polyominoes in enumerate(covers):
        if maxDraw is not None and i > maxDraw:
            break
        if i % perLine == 0:
            body += '\n\n'
        body += cover2tex(gridW, polyominoes, perLine, label='', clues=clues)
        body += '\\,'
    compileTeX(body, filename)

def drawDigits(polypartition, hookpartition, partialGrid = None):
    commands = ''
    if partialGrid is not None:
        for y in range(len(partialGrid)):
            for x in range(len(partialGrid[y])):
                dig = partialGrid[y][x]
                if dig != 0:
                    commands += '\\numbersquare{{{d}}}{{{x}}}{{{y}}}'.format(d=dig,x=x+1,y=y+1)
        return commands
        
    hdpartners = {h:d for d,h in hookpartition['dhpartners'].items()}
    for polyname, placement in polypartition.items():
        for (x,y) in placement:
            digit = hdpartners[hookpartition['hooks']['grid'][y][x]]
            commands += '\\numbersquare{{{d}}}{{{x}}}{{{y}}}'.format(d=digit,x=x+1,y=y+1)
    return commands

def drawFailedGrids(gridW, failedgrids, clues, filename, maxDraw = None):
    body = ''
    for i, failedgrid in enumerate(failedgrids):
        if maxDraw is not None and i > maxDraw:
            break
        cover, hpar, message, pgrid = failedgrid['cover'], failedgrid['hpartition'], failedgrid['message'], failedgrid['partialgrid']
        body += drawSolution(cover, hpar, clues, message, filename, returnBody = True, partialGrid = pgrid)
        body += '\n\n\\clearpage'
    compileTeX(body, filename)
    
def drawSolution(polyominopartition, hookpartition, clues, answer, filename, returnBody = False, partialGrid = None):
    gridW = len(hookpartition['corners'])+1
    label = (', '.join(['{}:{}'.format(d, h) for d, h in hookpartition['dhpartners'].items()]))
    body = '\\resizebox{30pc}{!}{\\begin{tikzpicture}\n'
    body += colorPolyominoes(polyominopartition)
    body += '\n    '.join(corners2paths(hookpartition['corners']))
    body += '\\drawgriddotted{{{}}}'.format(gridW)
    body += drawClues(clues, partialGrid)
    body += drawDigits(polyominopartition, hookpartition, partialGrid)
    body += '\\end{tikzpicture}}\n\\vspace{1pc}\n\n\\noindent'
    body += '\\Large{{\\tt {ans}}}'.format(ans = answer)
    if returnBody:
        return body
    compileTeX(body, filename)

    

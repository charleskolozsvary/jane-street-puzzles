import numpy as np
import utils.misc as misc

def cellsPictureCommand(cells):
    '''old version of what is now tikzCommand in net.py'''
    picture = ''
    orientation = 'canvas is xy plane at z = 0, transform shape, 3d view = {#1}{25}'
    picture += '\\newcommand{\\parampicture}[1]{\\begin{tikzpicture}'
    picture += '[{}]'.format(orientation)
    thickness = '1pt'
        
    for cell in cells:
        x, y, z = cell.corners[0]
        a = np.array(cell.corners[0])
        b = np.array(cell.corners[1])
        c = np.array(cell.corners[2])
        d = np.array(cell.corners[3])
            
        center_p = misc.np2Tuple(a + (c-a)/2)
            
        inside_a = misc.np2Tuple(a + (c-a)/5)
        inside_c = misc.np2Tuple(a + 4*(c-a)/5)
        inside_b = misc.np2Tuple(b + (d-b)/5)
        inside_d = misc.np2Tuple(b + 4*(d-b)/5)
        inside_path = [inside_a, inside_b, inside_c, inside_d]
            
        if cell.symbol:
            if cell.circled:
                picture += '\\node[circle,fill=gray,opacity=0.5,{}] at {} {{{}}};\n'.format(cell.canvas_spec,
                                                                                                center_p,
                                                                                                '\\LARGE $\\hphantom{\\mathsf{'+cell.symbol+'}}$')
                    
            picture += '\\node[{}] at {} {{{}}};\n'.format(cell.canvas_spec, center_p, '\\Large $\\mathsf{{{}}}$'.format(cell.symbol))
            picture += '\\draw[line width = {}] {}--cycle;\n'.format(thickness, '--'.join([str(c) for c in cell.corners]))
        else:
            picture += '\\fill[gray, opacity = 0.5] {}--cycle;\n'.format('--'.join([str(c) for c in cell.corners]))
            picture += '\\draw[line width = {}] {}--cycle;\n'.format(thickness, '--'.join([str(c) for c in cell.corners]))    

        if cell.squared:
            picture += '\\fill[color = gray, opacity = 0.5] {}--cycle;\n'.format('--'.join([str(c) for c in inside_path]))
            
    picture += '\\end{tikzpicture}}\n'

    return picture

def cellsPictureTeX(cells, fname, animate = False):
    with open('pictures/preamble.tex', 'r') as f:
        preamble = f.readlines()
    
    tex_file = ''.join(preamble)
    tex_file += cellsPictureCommand(cells)
    tex_file += '\\begin{document}\n'
    
    if animate:
        tex_file += '''\\begin{animateinline}{1}
        \\multiframe{90}{i=0+1}{\\parampicture{\\i}}
        \\end{animateinline}
        '''
    else:
        tex_file += '\\parampicture{20}'
    tex_file += '\\end{document}\n'
    with open('pictures/{}.tex'.format(fname), 'w') as f:
        f.write(tex_file)

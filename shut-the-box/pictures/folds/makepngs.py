import pymupdf

num_steps = 17

for i in range(num_steps+1):
    file_name = '{}debug.pdf'.format(i)
    doc = pymupdf.open(file_name)
    for pageno, page in enumerate(doc):
        print('lowres/step{}_{:03d}.png'.format(i, pageno))
        pix = page.get_pixmap(dpi = 220)
        pix.save('lowres/step{}_{:03d}.png'.format(i, pageno), jpg_quality = 50)


    

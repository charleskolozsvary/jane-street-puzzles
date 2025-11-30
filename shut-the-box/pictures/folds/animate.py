import os
import imageio.v2 as imageio
from copy import deepcopy

NUM_FRAMES = 360

FRAME_DIR = 'frames'

def makeAnimation(file_name_no_extension, frames_per_update, step_range = [0, 17]):
    frames = []
    for step in range(step_range[0], step_range[1]+1): # 0--17
        print(f'{step:02d}/{step_range[1]:02d}')
        chunk = step % (NUM_FRAMES // frames_per_update)
        start_page = chunk * frames_per_update
        end_page = start_page + frames_per_update
        for page in range(start_page, end_page):
            filename = os.path.join(FRAME_DIR, f"fold{step}_{page:03d}.png")
            if os.path.exists(filename):
                frames.append(imageio.imread(filename))
            else:
                print("Missing:", filename)

    # don't think this is necessary
    frames1 = deepcopy(frames)
    frames2 = deepcopy(frames)
    # save mp4
    imageio.mimsave(f'{file_name_no_extension}.mp4', frames1, fps=30)
    print(f"MP4 saved to {file_name_no_extension}.mp4")
    # save gif
    if frames_per_update < 180:
        imageio.mimsave(f'{file_name_no_extension}.gif', frames2, fps=30)
        print(f"GIF saved to {file_name_no_extension}.gif")

def animateShutBox(file_name_no_extension, file_stem):
    frames = []
    for page in range(0, 360):
        filename = os.path.join(FRAME_DIR, f"{file_stem}_{page:03d}.png")
        if os.path.exists(filename):
            frames.append(imageio.imread(filename))
        else:
            print("Missing:", filename)
    # save mp4
    imageio.mimsave(f'{file_name_no_extension}.mp4', frames, fps=30)
    print(f"MP4 saved to {file_name_no_extension}.mp4")
    # save gif
    imageio.mimsave(f'{file_name_no_extension}.gif', frames, fps=30)
    print(f"GIF saved to {file_name_no_extension}.gif")

def do17Folds():
    # # every 360
    # makeAnimation('animations/every180', 180)
    
    # every 90
    makeAnimation('animations/every90', 90)

    # every 45
    makeAnimation('animations/every45', 45)

    # every 30
    makeAnimation('animations/every30', 30)    

if __name__ == '__main__':
    do17Folds()
    # animateShutBox('animations/shutbox', 'box-complete')

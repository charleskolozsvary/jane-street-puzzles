import os
import imageio.v2 as imageio

import glob
import contextlib
from PIL import Image

FRAME_DIR = 'frames'

TOTAL_VIEWS_PER_FOLD = 360

def foldFrameFileNames(fold_name_prefix, extension, frames_per_fold, fold_step_range):
    frame_file_names = []
    for fold_step in range(fold_step_range[0], fold_step_range[1]+1):
        chunk = fold_step % (TOTAL_VIEWS_PER_FOLD // frames_per_fold)
        start_frame_idx = chunk * frames_per_fold
        end_frame_idx = start_frame_idx + frames_per_fold
        
        for idx in range(start_frame_idx, end_frame_idx):
            frame_file_name = os.path.join(FRAME_DIR, f'{fold_name_prefix}fold{fold_step}_{idx:03d}.{extension}')
            frame_file_names.append(frame_file_name)
    return frame_file_names

def animateShortPNGs(file_name_stem, frame_file_names, _duration):
    frames = []
    for i, frame_file_name in enumerate(frame_file_names):
        frames.append(Image.open(frame_file_name))

    frames[0].save(f'animations/{file_name_stem}.gif', format='GIF', save_all = True, append_images=frames[1:], duration=_duration, loop=0)
    print(f"wrote 'animations/{file_name_stem}.gif'")
    for img in frames:
        img.close()

def animatePNGs(file_name_stem, frame_file_names, _fps):
    if file_name_stem == 'full-every30': #or file_name_stem == 'ex-every30':
        animateShortPNGs(file_name_stem, frame_file_names, 1000/_fps)
        print('fps', _fps)
    return
        
    mp4_file_name = os.path.join('animations', f'{file_name_stem}.mp4')

    def saveAnimation(file_name): # not sure why .gif isn't working correctly
        with imageio.get_writer(file_name, mode='I', fps = _fps) as writer:
            for frame_file_name in frame_file_names:
                image = imageio.imread(frame_file_name)
                writer.append_data(image)    
    
    saveAnimation(mp4_file_name)
    print(f"\nMP4 saved to {mp4_file_name}\n")

def animateFolds(file_name_stem, fold_name_prefix, extension, frames_per_fold, fold_step_range, fps):
    frame_file_names = foldFrameFileNames(fold_name_prefix, extension, frames_per_fold, fold_step_range)
    animatePNGs(f'{file_name_stem}-every{frames_per_fold}', frame_file_names, fps)

if __name__ == '__main__':
    def ugh(stem, prefix, fold_range, per_angles, fpses):
        for i, angle in enumerate(per_angles):
            animateFolds(stem, prefix, 'png', angle, fold_range, fpses[i]) # 60 fps

    # ugh('ex', 'example-net-', [0, 12], [90, 60, 45, 30], [30, 30, 30, 23])
    # ugh('full', 'full-net-', [0, 17], [90, 60, 45, 30, 15], [30, 30, 30, 23, 20])

    # animateShortPNGs('static-example', [f'frames/static-example-net-fold{i}_000.png' for i in range(13)], 500)
    # animateShortPNGs('static-full', [f'frames/static-full-net-fold{i}_000.png' for i in range(18)], 500)

    # animateShortPNGs('static-example-fast', [f'frames/static-example-net-fold{i}_000.png' for i in range(13)], 200)
    # animateShortPNGs('static-full-fast', [f'frames/static-full-net-fold{i}_000.png' for i in range(18)], 200)

    # animateShortPNGs('static-example-veryfast', [f'frames/static-example-net-fold{i}_000.png' for i in range(13)], 100)
    # animateShortPNGs('static-full-veryfast', [f'frames/static-full-net-fold{i}_000.png' for i in range(18)], 100)

    animateShortPNGs('full-shutbox-360', [f'frames/full-net-fold17_{i:03d}.png' for i in range(360)], 33.333333)

    # in terminal: ulimit -n 1024

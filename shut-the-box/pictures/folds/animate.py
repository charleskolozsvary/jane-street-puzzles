import os
import imageio.v2 as imageio

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

def animatePNGs(file_name_stem, frame_file_names, _fps):
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
    example_prefix = 'example-net-'
    full_prefix = 'full-net-'
    
    animateFolds('example', example_prefix, 'png', 90, [0, 12], 60)
    animateFolds('example', example_prefix, 'png', 60, [0, 12], 60)
    animateFolds('example', example_prefix, 'png', 45, [0, 12], 60)
    animateFolds('example', example_prefix, 'png', 30, [0, 12], 60)

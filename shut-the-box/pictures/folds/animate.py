import os
from PIL import Image

num_steps = 17
chunk_size = 90    # frames per chunk
frame_dir = "lowres"    # folder where stepX_###.png are located

output_frames = []

for step in range(0, num_steps):
    print(step)
    chunk = (step - 1) % 4               # 0,1,2,3 repeating every 4 steps
    start_page = chunk * chunk_size      # 0, 90, 180, 270
    end_page = start_page + chunk_size   # up to 89, 179, 269, 359

    for page in range(start_page, end_page):
        
        filename = os.path.join(frame_dir, f"step{step}_{page:03d}.png")
        if os.path.exists(filename):
            img = Image.open(filename)
            output_frames.append(img.copy())
        else:
            print("Missing:", filename)

# print(output_frames)


output_frames[0].save(
    "folding.gif",
    save_all=True,
    append_images=output_frames[1:],
    duration=20,  # 30 fps
    loop=0
)

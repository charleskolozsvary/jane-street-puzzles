import os
from PIL import Image

num_steps = 17
num_frames = 360
frames_per_update = 45
chunk_size = frames_per_update
frame_dir = "lowres"    # folder where stepX_###.png are located

output_frames = []

for step in range(0, num_steps+1):
    print(step)
    chunk = step % (num_frames // frames_per_update)
    start_page = chunk * chunk_size      
    end_page = start_page + chunk_size   

    for page in range(start_page, end_page):
        
        filename = os.path.join(frame_dir, f"step{step}_{page:03d}.png")
        if os.path.exists(filename):
            img = Image.open(filename)
            output_frames.append(img.copy())
        else:
            print("Missing:", filename)

# print(output_frames)


output_frames[0].save(
    "30s45deg.gif",
    save_all=True,
    append_images=output_frames[1:],
    duration=30,  # 30 fps
    loop=0
)

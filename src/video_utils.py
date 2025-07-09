import numpy as np
import imageio.v2 as imageio
import tempfile
from PIL import Image, ImageDraw, ImageFont
import os


def add_z_text_to_frame(frame_array, z_val):
    if frame_array.ndim == 2:
        if frame_array.dtype != np.uint8:
            frame_array = np.clip(frame_array * 255, 0, 255).astype(np.uint8)
        img = Image.fromarray(frame_array).convert("RGB")

    elif frame_array.ndim == 3 and frame_array.shape[2] == 3:
        if frame_array.dtype != np.uint8:
            frame_array = np.clip(frame_array * 255, 0, 255).astype(np.uint8)
        img = Image.fromarray(frame_array, mode='RGB')

    draw = ImageDraw.Draw(img)
    text = f"z = {z_val:.3f} m"

    try:
        font_path = os.path.join("assets", "fonts", "DejaVuSans-Bold.ttf")
        font = ImageFont.truetype(font_path, size=24)
    except:
        font = ImageFont.load_default()

    width, height = img.size
    x = int(width * 0.03)
    y = int(height * 0.92)

    draw.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0))  
    draw.text((x, y), text, font=font, fill=(255, 255, 255))   

    return np.array(img)


def generate_video_from_arrays(image_list, fps, z_vals=None):
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmpfile:
        ruta = tmpfile.name
        frames = []

        for i, img in enumerate(image_list):
            z_val = z_vals[i] if z_vals is not None and i < len(z_vals) else None
            if z_val is not None:
                frame = add_z_text_to_frame(img, z_val)
            else:
                frame = img if img.dtype == np.uint8 else (np.clip(img * 255, 0, 255).astype(np.uint8))
            frames.append(frame)

        imageio.mimsave(ruta, frames, fps=fps, macro_block_size=None)
        return ruta

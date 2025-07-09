import numpy as np
from PIL import Image
from io import BytesIO

def load_rgb_channels(uploaded_file):
    img = Image.open(uploaded_file).convert('RGB')
    r, g, b = img.split()
    return np.array(r) / 255.0, np.array(g) / 255.0, np.array(b) / 255.0

def load_grayscale(uploaded_file):
    img = Image.open(uploaded_file).convert('L')
    return np.array(img) / 255.0

def load_image_auto_channels(uploaded_file):
    img = Image.open(uploaded_file)
    if img.mode == 'L':
        gray = load_grayscale(uploaded_file)
        return 'L', (gray,)
    else:
        r, g, b = load_rgb_channels(uploaded_file)
        return 'RGB', (r, g, b)

def recombine_rgb_channels(r, g, b):
    rgb = np.stack([r, g, b], axis=-1)
    return rgb

def normalize_result(result):
    result = np.abs(result)
    min_val = np.min(result)
    max_val = np.max(result)
    if max_val - min_val < 1e-12:
        return np.zeros_like(result)
    return (result - min_val) / (max_val - min_val)

def array_to_image_bytes(img_array):
    if np.iscomplexobj(img_array):
        img_array = np.abs(img_array)

    if img_array.ndim == 2:
        img_array = np.clip(img_array * 255, 0, 255).astype(np.uint8)
        img = Image.fromarray(img_array, mode='L')

    elif img_array.ndim == 3 and img_array.shape[2] == 3:
        if img_array.dtype != np.uint8:
            img_array = np.clip(img_array * 255, 0, 255).astype(np.uint8)
        img = Image.fromarray(img_array, mode='RGB')

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


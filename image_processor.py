import os
import numpy as np
from PIL import Image
from jpeg_core import compress_image

def calculate_mse(original, compressed):
    mse_val = np.mean((original.astype(np.float32) - compressed.astype(np.float32)) ** 2)
    return float(mse_val)

def get_file_size_kb(filepath):
    return os.path.getsize(filepath) / 1024

def process_full_pipeline(input_path, output_dir):
    img = np.array(Image.open(input_path).convert('RGB'))
    original_size = float(get_file_size_kb(input_path))
    filename = os.path.basename(input_path).split('.')[0]
    
    results = []
    for q in range(10, 110, 10):
        compressed_img = compress_image(img, q)
        out_filename = f"{filename}_q{q}.png"
        out_path = os.path.join(output_dir, out_filename)
        
        # Save as PNG as requested
        Image.fromarray(compressed_img).save(out_path)
        
        file_size = get_file_size_kb(out_path)
        results.append({
            "quality": q,
            "filename": out_filename,
            "file_size_kb": round(file_size, 2),
            "size_percent": round((file_size / original_size) * 100, 2),
            "mse": round(calculate_mse(img, compressed_img), 2)
        })
    return results, original_size

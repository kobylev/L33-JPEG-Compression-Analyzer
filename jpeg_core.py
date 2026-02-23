import numpy as np
from scipy.fft import dctn, idctn

# Standard JPEG Quantization Tables
LUM_TABLE = np.array([
    [16, 11, 10, 16, 24, 40, 51, 61], [12, 12, 14, 19, 26, 58, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56], [14, 17, 22, 29, 51, 87, 80, 62],
    [18, 22, 37, 56, 68, 109, 103, 77], [24, 35, 55, 64, 81, 104, 113, 92],
    [49, 64, 78, 87, 103, 121, 120, 101], [72, 92, 95, 98, 112, 100, 103, 99]
])

CHR_TABLE = np.array([
    [17, 18, 24, 47, 99, 99, 99, 99], [18, 21, 26, 66, 99, 99, 99, 99],
    [24, 26, 56, 99, 99, 99, 99, 99], [47, 66, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99], [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99], [99, 99, 99, 99, 99, 99, 99, 99]
])

def get_quantization_table(table, quality):
    scale = 5000 / quality if quality < 50 else 200 - 2 * quality
    q_table = np.floor((table * scale + 50) / 100)
    return np.clip(q_table, 1, 255)

def rgb_to_ycbcr(img):
    r, g, b = img[:,:,0], img[:,:,1], img[:,:,2]
    y = 0.299 * r + 0.587 * g + 0.114 * b
    cb = -0.1687 * r - 0.3313 * g + 0.5 * b + 128
    cr = 0.5 * r - 0.4187 * g - 0.0813 * b + 128
    return np.stack([y, cb, cr], axis=-1)

def ycbcr_to_rgb(img):
    y, cb, cr = img[:,:,0], img[:,:,1], img[:,:,2]
    r = y + 1.402 * (cr - 128)
    g = y - 0.344136 * (cb - 128) - 0.714136 * (cr - 128)
    b = y + 1.772 * (cb - 128)
    return np.clip(np.stack([r, g, b], axis=-1), 0, 255).astype(np.uint8)

def process_block(block, q_table):
    # 2D DCT
    dct_block = dctn(block, norm='ortho')
    # Quantize
    quant_block = np.round(dct_block / q_table)
    # Dequantize
    dequant_block = quant_block * q_table
    # 2D IDCT
    return idctn(dequant_block, norm='ortho')

def compress_image(img, quality):
    h, w, _ = img.shape
    new_h, new_w = (h + 7) // 8 * 8, (w + 7) // 8 * 8
    padded = np.zeros((new_h, new_w, 3))
    padded[:h, :w, :] = img
    
    ycbcr = rgb_to_ycbcr(padded)
    q_lum = get_quantization_table(LUM_TABLE, quality)
    q_chr = get_quantization_table(CHR_TABLE, quality)
    
    output = np.zeros_like(ycbcr)
    for c in range(3):
        q_table = q_lum if c == 0 else q_chr
        for i in range(0, new_h, 8):
            for j in range(0, new_w, 8):
                output[i:i+8, j:j+8, c] = process_block(ycbcr[i:i+8, j:j+8, c], q_table)
                
    return ycbcr_to_rgb(output)[:h, :w, :]

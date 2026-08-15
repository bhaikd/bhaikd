import sys
import os
import cv2
import numpy as np
from PIL import Image
from io import BytesIO

def prep_photo(input_path, output_path="source-prepped.png"):
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        sys.exit(1)

    try:
        from rembg import remove
    except ImportError:
        print("Error: The 'rembg' package is not installed in your current Python environment.")
        print("Please activate the virtual environment or install it using:")
        print("    pip install -r scripts/requirements.txt")
        sys.exit(1)

    print(f"Removing background from '{input_path}' using rembg...")
    with open(input_path, "rb") as f:
        input_bytes = f.read()
    
    output_bytes = remove(input_bytes)
    rgba_img = Image.open(BytesIO(output_bytes)).convert("RGBA")
    
    np_img = np.array(rgba_img)
    rgb = np_img[:, :, :3]
    alpha = np_img[:, :, 3]

    # Convert RGB to Grayscale
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced_gray = clahe.apply(gray)

    # Composite onto pure white background so alpha=0 maps to white (blank space)
    alpha_norm = alpha.astype(float) / 255.0
    composite = (enhanced_gray.astype(float) * alpha_norm + 255.0 * (1.0 - alpha_norm)).astype(np.uint8)

    # Save as grayscale PNG
    prepped_pil = Image.fromarray(composite, mode="L")
    prepped_pil.save(output_path)
    print(f"Prepped image saved successfully to '{output_path}'.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    elif os.path.exists("profile.jpg"):
        input_file = "profile.jpg"
    elif os.path.exists("source-photo.jpg"):
        input_file = "source-photo.jpg"
    else:
        print("Usage: python scripts/prep_photo.py <source-photo.jpg> [output-path.png]")
        sys.exit(1)
    
    out_file = sys.argv[2] if len(sys.argv) > 2 else "source-prepped.png"
    prep_photo(input_file, out_file)


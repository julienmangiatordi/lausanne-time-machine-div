#!/usr/bin/env python3
"""
Convert GeoTIFF to PNG using OpenCV (cv2).
OpenCV peut lire les fichiers TIFF sans les limitations de PIL.
"""

from pathlib import Path
import sys
import cv2
import numpy as np

def convert_tif_to_png(tif_path, output_dir='assets/images'):
    """Convert TIF to PNG using OpenCV."""
    tif_path = Path(tif_path)
    output_dir = Path(output_dir)
    
    if not tif_path.exists():
        print(f"❌ File not found: {tif_path}")
        return False
    
    png_path = output_dir / (tif_path.stem + '.png')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📍 Converting: {tif_path.name}")
    print(f"   → PNG: {png_path}")
    
    try:
        # Read TIFF with OpenCV
        img = cv2.imread(str(tif_path), cv2.IMREAD_UNCHANGED)
        
        if img is None:
            print(f"❌ Failed to read file with OpenCV")
            return False
        
        print(f"   Shape: {img.shape}")
        print(f"   Dtype: {img.dtype}")
        
        # Handle different formats
        if len(img.shape) == 3:
            # Multi-channel image
            if img.shape[2] == 4:
                # RGBA - convert to RGB
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            elif img.shape[2] == 3:
                # BGR (OpenCV default) - convert to RGB for PNG
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        else:
            # Grayscale - convert to RGB
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        
        # Normalize if needed
        if img.dtype != np.uint8:
            # Scale to 0-255
            img_min = img.min()
            img_max = img.max()
            if img_max > img_min:
                img = ((img - img_min) / (img_max - img_min) * 255).astype(np.uint8)
            else:
                img = img.astype(np.uint8)
        
        # Save as PNG
        success = cv2.imwrite(str(png_path), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        
        if success:
            print(f"✓ PNG saved: {png_path}")
            print(f"  Dimensions: {img.shape[1]}x{img.shape[0]} pixels")
            return True
        else:
            print(f"❌ Failed to write PNG")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 convert_cv2.py <file.tif> [output_dir]")
        print("\nExample:")
        print("  python3 convert_cv2.py assets/images/1923.tif assets/images")
        sys.exit(1)
    
    tif_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'assets/images'
    
    success = convert_tif_to_png(tif_file, output_dir)
    sys.exit(0 if success else 1)

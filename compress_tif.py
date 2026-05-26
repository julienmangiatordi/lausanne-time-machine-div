#!/usr/bin/env python3
"""
Compress and convert GeoTIFF to PNG.
Réduit la résolution du TIF pour éviter les limites de PIL,
puis convertit en PNG.
"""

from pathlib import Path
import sys
import os
from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # Remove PIL's decompression bomb limit

def compress_and_convert_tif(tif_path, output_dir='assets/images', max_width=4096, invert=False, contrast=1.0):
    """Compress TIF and convert to PNG."""
    tif_path = Path(tif_path)
    output_dir = Path(output_dir)
    
    if not tif_path.exists():
        print(f"❌ File not found: {tif_path}")
        return False
    
    png_path = output_dir / (tif_path.stem + '.png')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📍 Processing: {tif_path.name}")
    print(f"   File size: {tif_path.stat().st_size / (1024**2):.1f} MB")
    
    try:
        # Open TIFF
        print(f"   Opening TIF...")
        img = Image.open(tif_path)
        
        print(f"   Original size: {img.width}x{img.height}")
        print(f"   Format: {img.format}, Mode: {img.mode}")
        
        # Resize if too large
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            print(f"   Resizing to: {max_width}x{new_height}")
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Convert to RGB first (before invert/contrast operations)
        if img.mode not in ('RGB', 'L'):
            print(f"   Converting mode {img.mode} → RGB")
            if img.mode == 'RGBA':
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            elif img.mode == 'P':
                # Palette mode - convert to RGB
                img = img.convert('RGB')
            else:
                img = img.convert('RGB')
        
        # Ensure grayscale is RGB
        if img.mode == 'L':
            img = img.convert('RGB')
        
        # Invert colors if requested
        if invert:
            print(f"   Inverting colors...")
            if img.mode == 'RGB':
                from PIL import ImageOps
                img = ImageOps.invert(img)
        
        # Increase contrast if requested
        if contrast != 1.0:
            from PIL import ImageEnhance
            print(f"   Increasing contrast ({contrast}x)...")
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast)
        
        # Save as PNG
        print(f"   Saving PNG to: {png_path}")
        img.save(png_path, 'PNG', optimize=True)
        
        file_size = png_path.stat().st_size / (1024**2)
        print(f"✓ PNG created: {file_size:.1f} MB")
        print(f"  Dimensions: {img.width}x{img.height}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 compress_tif.py <file.tif> [output_dir] [max_width] [--invert] [--contrast FACTOR]")
        print("\nExample:")
        print("  python3 compress_tif.py assets/images/1951.tif assets/images")
        print("  python3 compress_tif.py assets/images/1951.tif assets/images 3000")
        print("  python3 compress_tif.py assets/images/1951.tif assets/images 3000 --invert")
        print("  python3 compress_tif.py assets/images/1951.tif assets/images 3000 --invert --contrast 1.5")
        print("\nDefaults:")
        print("  - output_dir: assets/images")
        print("  - max_width: 4096 pixels")
        print("  - invert: False (add --invert flag to invert colors)")
        print("  - contrast: 1.0 (1.0 = normal, 1.5 = 50% more contrast, 2.0 = double contrast)")
        sys.exit(1)
    
    tif_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'assets/images'
    max_width = 4096
    invert = False
    contrast = 1.0
    
    # Parse remaining arguments
    for i in range(3, len(sys.argv)):
        arg = sys.argv[i]
        if arg.isdigit():
            max_width = int(arg)
        elif arg == '--invert':
            invert = True
        elif arg == '--contrast' and i + 1 < len(sys.argv):
            contrast = float(sys.argv[i + 1])
    
    success = compress_and_convert_tif(tif_file, output_dir, max_width, invert, contrast)
    sys.exit(0 if success else 1)

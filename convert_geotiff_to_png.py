#!/usr/bin/env python3
"""
Convert GeoTIFF files to PNG + worldfile (.pgw) for web overlay.
Uses PIL/Pillow to read TIFF tags and extract georeference.

Usage:
    python3 convert_geotiff_to_png.py
    
This will look for *.tif files in assets/images/ and convert each to PNG + .pgw worldfile.
"""

from pathlib import Path
from PIL import Image
import struct
import sys

def extract_geotiff_info(tif_path):
    """Extract georeference info from GeoTIFF using PIL TIFF tags."""
    try:
        img = Image.open(tif_path)
        
        # TIFF tags for georeference
        # 33550 = ModelPixelScaleTag (pixel size)
        # 33922 = ModelTiepointTag (origin)
        
        if not hasattr(img, 'tag_v2'):
            return None
        
        tags = img.tag_v2
        
        # Get pixel scale (tag 33550)
        pixel_scale = tags.get(33550)
        if not pixel_scale:
            return None
        
        # Get tiepoint (tag 33922)
        tiepoint = tags.get(33922)
        if not tiepoint:
            return None
        
        # pixel_scale = (scaleX, scaleY, scaleZ) - typically (pixelWidth, -pixelHeight, 0)
        scale_x = pixel_scale[0]
        scale_y = pixel_scale[1] if len(pixel_scale) > 1 else pixel_scale[0]
        
        # tiepoint = (I, J, K, X, Y, Z) where (I,J,K) is pixel coords, (X,Y,Z) is geo coords
        # Typically: (0, 0, 0, originX, originY, 0)
        origin_x = tiepoint[3]
        origin_y = tiepoint[4]
        
        width = img.width
        height = img.height
        
        return {
            'width': width,
            'height': height,
            'scale_x': scale_x,
            'scale_y': scale_y,
            'origin_x': origin_x,
            'origin_y': origin_y,
        }
    except Exception as e:
        print(f"Error extracting georeference: {e}")
        return None

def convert_geotiff_to_png(tif_path, output_dir=None):
    """Convert a GeoTIFF to PNG + worldfile using PIL."""
    if output_dir is None:
        output_dir = 'assets/images'
    output_dir = Path(output_dir)
    tif_path = Path(tif_path)
    
    if not tif_path.exists():
        print(f"❌ File not found: {tif_path}")
        return False
    
    png_name = tif_path.stem + '.png'
    png_path = output_dir / png_name
    pgw_path = output_dir / (tif_path.stem + '.pgw')
    
    print(f"\n📍 Converting: {tif_path.name}")
    print(f"   → PNG: {png_path}")
    print(f"   → Worldfile: {pgw_path}")
    
    try:
        # Extract georeference info
        geo_info = extract_geotiff_info(tif_path)
        if not geo_info:
            print("⚠️  Could not extract georeference from GeoTIFF")
            return False
        
        # Open and convert TIFF to PNG
        img = Image.open(tif_path)
        
        # Convert to RGB if necessary (remove alpha, indexed colors, etc.)
        if img.mode in ('RGBA', 'LA', 'P'):
            # Convert with white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Save as PNG
        img.save(png_path, 'PNG')
        print(f"✓ PNG created ({geo_info['width']}x{geo_info['height']})")
        
        # Create worldfile
        # Format: 6 lines
        # pixelSizeX, rotX, rotY, pixelSizeY, originX, originY
        worldfile_content = (
            f"{geo_info['scale_x']}\n"
            f"0\n"
            f"0\n"
            f"{geo_info['scale_y']}\n"
            f"{geo_info['origin_x']}\n"
            f"{geo_info['origin_y']}\n"
        )
        
        with open(pgw_path, 'w') as f:
            f.write(worldfile_content)
        
        print(f"✓ Worldfile created: {pgw_path}")
        print(f"  Pixel size: ({geo_info['scale_x']}, {geo_info['scale_y']})")
        print(f"  Origin: ({geo_info['origin_x']}, {geo_info['origin_y']})")
        return True
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Convert all .tif files in assets/images/ to PNG + .pgw."""
    input_dir = Path('assets/images')
    
    if not input_dir.exists():
        print(f"❌ Directory not found: {input_dir}")
        print("   Create it first: mkdir -p assets/images")
        sys.exit(1)
    
    tif_files = list(input_dir.glob('*.tif')) + list(input_dir.glob('*.TIF'))
    
    if not tif_files:
        print(f"❌ No .tif files found in {input_dir}")
        sys.exit(1)
    
    print(f"🔍 Found {len(tif_files)} GeoTIFF file(s)")
    
    success_count = 0
    for tif_file in sorted(tif_files):
        if convert_geotiff_to_png(tif_file, input_dir):
            success_count += 1
    
    print(f"\n{'='*50}")
    print(f"✓ Converted {success_count}/{len(tif_files)} file(s)")
    print(f"\nNext steps:")
    print(f"1. Start the server: python3 -m http.server 8000")
    print(f"2. Open http://localhost:8000")
    print(f"3. The map overlays should now appear and toggle in the layers control")

if __name__ == '__main__':
    main()

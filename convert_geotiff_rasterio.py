#!/usr/bin/env python3
"""
Convert GeoTIFF files to PNG using rasterio (better GeoTIFF support).

Usage:
    python3 convert_geotiff_rasterio.py 1923.tif
"""

from pathlib import Path
import sys

try:
    import rasterio
    from rasterio.plot import show
    import numpy as np
    from PIL import Image
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("   Install: pip install rasterio pillow numpy")
    sys.exit(1)


def convert_tif_to_png(tif_path, output_dir='assets/images'):
    """Convert GeoTIFF to PNG using rasterio."""
    tif_path = Path(tif_path)
    output_dir = Path(output_dir)
    
    if not tif_path.exists():
        print(f"❌ File not found: {tif_path}")
        return False
    
    png_path = output_dir / (tif_path.stem + '.png')
    
    print(f"\n📍 Converting: {tif_path.name}")
    print(f"   → PNG: {png_path}")
    
    try:
        # Open with rasterio
        with rasterio.open(tif_path) as src:
            print(f"   Width: {src.width}, Height: {src.height}")
            print(f"   CRS: {src.crs}")
            print(f"   Bounds: {src.bounds}")
            
            # Read all bands
            data = src.read()
            
            # Handle different band configurations
            if src.count == 1:
                # Grayscale
                band_data = data[0]
            elif src.count >= 3:
                # RGB or RGBA
                band_data = data[:3].transpose(1, 2, 0)
            else:
                print(f"⚠️  Unsupported band count: {src.count}")
                return False
            
            # Normalize to 0-255
            if band_data.dtype != np.uint8:
                band_data = band_data.astype(np.float32)
                vmin, vmax = np.nanpercentile(band_data, [2, 98])
                band_data = np.clip((band_data - vmin) / (vmax - vmin) * 255, 0, 255).astype(np.uint8)
            
            # Convert to PIL and save
            if src.count == 1:
                img = Image.fromarray(band_data, mode='L').convert('RGB')
            else:
                img = Image.fromarray(band_data, mode='RGB')
            
            img.save(png_path, 'PNG')
            print(f"✓ PNG created: {png_path}")
            print(f"  Size: {img.size[0]}x{img.size[1]} pixels")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 convert_geotiff_rasterio.py <file.tif> [output_dir]")
        print("\nExample:")
        print("  python3 convert_geotiff_rasterio.py 1923.tif assets/images")
        sys.exit(1)
    
    tif_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'assets/images'
    
    success = convert_tif_to_png(tif_file, output_dir)
    
    if success:
        print(f"\n✓ Conversion complete!")
        print(f"  PNG file: {Path(output_dir) / (Path(tif_file).stem + '.png')}")
    else:
        print(f"\n❌ Conversion failed")
        sys.exit(1)

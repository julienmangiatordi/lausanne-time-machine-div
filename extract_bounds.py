#!/usr/bin/env python3
"""
Extract bounds from WGS84 GeoTIFF and save as JSON for web use
"""
from PIL import Image
import json
from pathlib import Path

def extract_bounds_from_geotiff(tif_path):
    """Extract geographic bounds from a GeoTIFF file"""
    try:
        # Try different approaches to read the TIFF
        print(f"Attempting to read {tif_path}...")
        
        # Approach 1: Direct PIL open with plugins
        img = Image.open(tif_path)
        img.load()  # Force load
        
        print(f"✓ Image loaded: {img.width}x{img.height}, mode: {img.mode}")
        
        # Try to extract georeference tags
        if hasattr(img, 'tag_v2'):
            tags = img.tag_v2
            
            # Tag 33550: ModelPixelScaleTag
            if 33550 in tags:
                scale = tags[33550]
                print(f"  Pixel scale: {scale}")
            
            # Tag 33922: ModelTiepointTag
            if 33922 in tags:
                tiepoint = tags[33922]
                print(f"  Tiepoint: {tiepoint}")
                
                if len(tiepoint) >= 6:
                    # (I, J, K, X, Y, Z) where X,Y are geo coordinates
                    origin_x = tiepoint[3]
                    origin_y = tiepoint[4]
                    
                    if 33550 in tags:
                        pixel_x = scale[0]
                        pixel_y = scale[1] if len(scale) > 1 else scale[0]
                        
                        # Calculate bounds (assuming these are already in WGS84)
                        east = origin_x + img.width * pixel_x
                        south = origin_y + img.height * pixel_y
                        west = origin_x
                        north = origin_y
                        
                        print(f"\n✓ Bounds extracted:")
                        print(f"  North: {north}")
                        print(f"  South: {south}")
                        print(f"  West: {west}")
                        print(f"  East: {east}")
                        
                        # Return in Leaflet format [[south, west], [north, east]]
                        return [[south, west], [north, east]]
        
        print("⚠️  Could not extract georeference tags")
        return None
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    input_file = Path('assets/images/1838_4326.tif')
    
    if not input_file.exists():
        print(f"❌ File not found: {input_file}")
        return
    
    bounds = extract_bounds_from_geotiff(input_file)
    
    if bounds:
        # Save bounds to JSON
        output_file = Path('assets/images/bounds.json')
        with open(output_file, 'w') as f:
            json.dump({
                '1832': bounds
            }, f, indent=2)
        
        print(f"\n✓ Bounds saved to {output_file}")
        print(f"Use in JavaScript: [[{bounds[0][0]}, {bounds[0][1]}], [{bounds[1][0]}, {bounds[1][1]}]]")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Test conversion UTM / Swiss coordinates to lat/lon
"""
import math

def utm32_to_latlon(easting, northing):
    """Convert UTM zone 32N to lat/lon (WGS84)"""
    # UTM zone 32N parameters
    a = 6378137.0  # WGS84 semi-major axis
    e2 = 0.00669438  # WGS84 eccentricity squared
    e_prime2 = e2 / (1 - e2)
    k0 = 0.9996  # scale factor
    lon0 = 9.0  # central meridian for zone 32N
    
    m = northing / k0
    mu = m / (a * (1 - e2/4 - 3*e2*e2/64 - 5*e2*e2*e2/256))
    
    phi1 = mu + (3*e2/8 + 3*e2*e2/32 - 45*e2*e2*e2/1024) * math.sin(2*mu)
    phi1 += (15*e2*e2/256 + 45*e2*e2*e2/1024) * math.sin(4*mu)
    phi1 -= (35*e2*e2*e2/3072) * math.sin(6*mu)
    
    c1 = e_prime2 * (math.cos(phi1) ** 2)
    t1 = (math.tan(phi1)) ** 2
    n1 = a / math.sqrt(1 - e2 * (math.sin(phi1) ** 2))
    r1 = a * (1 - e2) / math.sqrt((1 - e2 * (math.sin(phi1) ** 2)) ** 3)
    
    d = easting / (n1 * k0)
    
    lat = phi1 - (t1/r1) * (d*d/2 - (d**4/24)*(5 + 3*t1 + 10*c1 - 4*c1*c1 - 9*e_prime2)
                           + (d**6/720)*(61 + 90*t1 + 28*t1*t1))
    
    lon = (d - (d**3/6)*(1 + 2*t1 + c1) + (d**5/120)*(5 - 2*c1 + 28*t1 - 3*c1*c1 + 8*e_prime2 + 24*t1*t1)) / math.cos(phi1)
    
    return math.degrees(lat), lon0 + math.degrees(lon)

def swiss_lv95_to_latlon(easting, northing):
    """
    Convert Swiss LV95 coordinates (EPSG:2056) to lat/lon
    Using a simple approximation
    """
    # Swiss LV95 is based on UTM zone 32N with false easting/northing
    # False Easting: 2683141.94 m
    # False Northing: 1247057.51 m
    
    # Remove false easting/northing
    e_utm = easting - 2683141.94
    n_utm = northing - 1247057.51
    
    # Convert UTM to lat/lon
    return utm32_to_latlon(e_utm, n_utm)

# Test with your coordinates
print("Testing conversion for 1832.tif:")
print()

coords = [2534732.4941, 1155982.7257]
print(f"Input coordinates (from worldfile): {coords}")
print()

# Try Swiss LV95 conversion
lat, lon = swiss_lv95_to_latlon(coords[0], coords[1])
print(f"Swiss LV95 → lat/lon: {lat:.6f}, {lon:.6f}")
print()

# Also try direct UTM
lat, lon = utm32_to_latlon(coords[0], coords[1])
print(f"Direct UTM32N → lat/lon: {lat:.6f}, {lon:.6f}")
print()

print("Expected Lausanne area: ~46.52 lat, ~6.63 lon")

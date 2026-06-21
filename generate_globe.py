import json
import urllib.request
import math

def point_in_polygon(point, polygon):
    x, y = point
    inside = False
    n = len(polygon)
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def point_in_feature(point, feature):
    geom = feature['geometry']
    t = geom['type']
    coords = geom['coordinates']
    
    if t == 'Polygon':
        if not point_in_polygon(point, coords[0]):
            return False
        for hole in coords[1:]:
            if point_in_polygon(point, hole):
                return False
        return True
    elif t == 'MultiPolygon':
        for poly in coords:
            if point_in_polygon(point, poly[0]):
                in_hole = False
                for hole in poly[1:]:
                    if point_in_polygon(point, hole):
                        in_hole = True
                        break
                if not in_hole:
                    return True
        return False
    return False

def main():
    print("Fetching land map data...")
    url = "https://raw.githubusercontent.com/martynafford/natural-earth-geojson/refs/heads/master/110m/physical/ne_110m_land.json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        
    print("Generating dot grid...")
    dots = []
    # Step sizes (adjust spacing of dots)
    # Spacing of 4 degrees gives a detailed but lightweight grid
    step_lng = 4.0
    step_lat = 4.0
    
    # Generate dots on land features
    for feature in data['features']:
        # Simple bounding box check to speed things up
        geom = feature['geometry']
        flat_coords = []
        if geom['type'] == 'Polygon':
            flat_coords = [p for ring in geom['coordinates'] for p in ring]
        elif geom['type'] == 'MultiPolygon':
            flat_coords = [p for poly in geom['coordinates'] for ring in poly for p in ring]
            
        if not flat_coords:
            continue
            
        lngs = [p[0] for p in flat_coords]
        lats = [p[1] for p in flat_coords]
        min_lng, max_lng = min(lngs), max(lngs)
        min_lat, max_lat = min(lats), max(lats)
        
        # Round to step grid
        start_lng = math.floor(min_lng / step_lng) * step_lng
        end_lng = math.ceil(max_lng / step_lng) * step_lng
        start_lat = math.floor(min_lat / step_lat) * step_lat
        end_lat = math.ceil(max_lat / step_lat) * step_lat
        
        lng = start_lng
        while lng <= end_lng:
            lat = start_lat
            while lat <= end_lat:
                point = (lng, lat)
                if point_in_feature(point, feature):
                    dots.append(point)
                lat += step_lat
            lng += step_lng

    # Deduplicate dots (points on boundary checks might overlap)
    unique_dots = list(set(dots))
    print(f"Generated {len(unique_dots)} unique land dots.")
    
    # Map width and height for projection
    # We will map -180 to 180 longitude to 0 to 600 width
    # And -90 to 90 latitude to 300 to 0 height (y is inverted in SVG)
    map_width = 600
    map_height = 300
    
    svg_dots = []
    for lng, lat in unique_dots:
        # Equirectangular projection coordinates
        x = (lng + 180) * (map_width / 360.0)
        y = (90 - lat) * (map_height / 180.0)
        svg_dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.5" />')
        
    dots_group_content = "\n    ".join(svg_dots)
    
    # SVG Boilerplate with clipPath, dual group translation animation, and spherical shading overlay
    svg_template = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 300" width="100%" height="100%">
  <defs>
    <!-- Ocean background gradient -->
    <radialGradient id="ocean" cx="50%" cy="50%" r="50%">
      <stop offset="70%" stop-color="#070a13" />
      <stop offset="100%" stop-color="#020305" />
    </radialGradient>

    <!-- 3D Sphere Shading Overlay -->
    <radialGradient id="sphere-shadow" cx="40%" cy="40%" r="60%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.1" />
      <stop offset="50%" stop-color="#000000" stop-opacity="0" />
      <stop offset="85%" stop-color="#020305" stop-opacity="0.7" />
      <stop offset="100%" stop-color="#020305" stop-opacity="0.95" />
    </radialGradient>

    <!-- Globe Grid Overlay (Graticules) -->
    <radialGradient id="grid-glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#6366f1" stop-opacity="0.25" />
      <stop offset="100%" stop-color="#6366f1" stop-opacity="0.05" />
    </radialGradient>

    <!-- Clip path to shape the translating flat map into a circular globe -->
    <clipPath id="globe-clip">
      <circle cx="150" cy="150" r="100" />
    </clipPath>

    <style>
      .bg {{
        fill: transparent;
      }}
      .globe-border {{
        fill: none;
        stroke: #334155;
        stroke-width: 1.5;
        stroke-opacity: 0.6;
      }}
      .land-dots {{
        fill: #06b6d4;
        opacity: 0.85;
      }}
      .graticule {{
        fill: none;
        stroke: #1e293b;
        stroke-width: 0.5;
        stroke-opacity: 0.6;
      }}
      
      /* Animates the two map groups moving horizontally */
      .map-group {{
        animation: spin 16s linear infinite;
      }}
      
      @keyframes spin {{
        0% {{
          transform: translateX(0px);
        }}
        100% {{
          transform: translateX(-{map_width}px);
        }}
      }}
    </style>
  </defs>

  <rect width="100%" height="100%" class="bg" />

  <!-- The Globe Container -->
  <g clip-path="url(#globe-clip)">
    <!-- 1. Globe Ocean Base -->
    <circle cx="150" cy="150" r="100" fill="url(#ocean)" />

    <!-- 2. Grid lines (Graticules) -->
    <!-- Latitudes -->
    <circle cx="150" cy="150" r="85" class="graticule" />
    <circle cx="150" cy="150" r="65" class="graticule" />
    <circle cx="150" cy="150" r="40" class="graticule" />
    <circle cx="150" cy="150" r="15" class="graticule" />
    <!-- Longitudes (drawn as ellipses) -->
    <ellipse cx="150" cy="150" rx="80" ry="100" class="graticule" />
    <ellipse cx="150" cy="150" rx="60" ry="100" class="graticule" />
    <ellipse cx="150" cy="150" rx="40" ry="100" class="graticule" />
    <ellipse cx="150" cy="150" rx="20" ry="100" class="graticule" />
    <line x1="150" y1="50" x2="150" y2="250" class="graticule" />
    <line x1="50" y1="150" x2="250" y2="150" class="graticule" />

    <!-- 3. Translating Dotted Map Group -->
    <!-- We stack two identical maps side by side (0px and 600px) so the translation loops seamlessly -->
    <g class="map-group land-dots" transform="translate(0, 0)">
      <g id="map-single">
        {dots_group_content}
      </g>
      <g id="map-duplicate" transform="translate({map_width}, 0)">
        {dots_group_content}
      </g>
    </g>

    <!-- 4. Spherical Shading Overlay for 3D depth -->
    <circle cx="150" cy="150" r="100" fill="url(#sphere-shadow)" />
  </g>

  <!-- Globe Outline -->
  <circle cx="150" cy="150" r="100" class="globe-border" />
</svg>
"""

    with open("globe.svg", "w") as f:
        f.write(svg_template)
    print("Successfully generated globe.svg!")

if __name__ == "__main__":
    main()

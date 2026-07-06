import sqlite3, json, struct
from shapely import wkb
from shapely.geometry import mapping

con = sqlite3.connect('db/vector_earth.db')
row = con.execute('SELECT geometry FROM countries WHERE name = ?', ('Singapore',)).fetchone()
con.close()

hex_str = row[0]
raw = bytes.fromhex(hex_str)

print('=== 1. Raw WKB hex ===')
print(f'  First 80 chars : {hex_str[:80]} ...')
print(f'  Total length   : {len(hex_str)} hex chars = {len(hex_str)//2} bytes')

print()
print('=== 2. WKB byte layout (manual decode) ===')
endian = 'little-endian' if raw[0] == 1 else 'big-endian'
print(f'  Byte 0  (endian flag)    : 0x{raw[0]:02X}  -> {endian}')
geom_type = struct.unpack_from('<I', raw, 1)[0]
wkb_types = {1: 'Point', 2: 'LineString', 3: 'Polygon', 4: 'MultiPoint',
             5: 'MultiLineString', 6: 'MultiPolygon', 7: 'GeometryCollection'}
print(f'  Bytes 1-4 (geometry type): {geom_type}  -> {wkb_types.get(geom_type, "unknown")}')
num_rings = struct.unpack_from('<I', raw, 5)[0]
print(f'  Bytes 5-8 (num rings)    : {num_rings}  (ring 0 = exterior, rest = holes)')
num_pts = struct.unpack_from('<I', raw, 9)[0]
print(f'  Bytes 9-12 (ring 0 pts)  : {num_pts}  (each point = 16 bytes: lon f64 + lat f64)')
print(f'  Expected total size      : 9 header + 4 ring-count + {num_pts}*16 coords')
print(f'                           = {9 + 4 + num_pts * 16} bytes  (actual: {len(raw)} bytes)')

print()
geom = wkb.loads(raw)
print('=== 3. Shapely geometry ===')
print(f'  Type           : {geom.geom_type}')
print(f'  Interior rings : {len(list(geom.interiors))}  (holes in the polygon)')
ext_pts = len(geom.exterior.coords)
print(f'  Exterior points: {ext_pts}  (first == last, so {ext_pts - 1} unique vertices)')
b = geom.bounds
print(f'  Bounding box   : minLon={b[0]:.6f}  minLat={b[1]:.6f}  maxLon={b[2]:.6f}  maxLat={b[3]:.6f}')

print()
print('=== 4. All coordinate pairs (lon, lat) ===')
for i, (lon, lat) in enumerate(geom.exterior.coords):
    marker = ' <- closes ring (same as [0])' if i == ext_pts - 1 else ''
    print(f'  [{i:>2}]  lon={lon:.6f}  lat={lat:.6f}{marker}')

print()
print('=== 5. GeoJSON (as sent to the browser) ===')
print(json.dumps(mapping(geom), indent=2))
